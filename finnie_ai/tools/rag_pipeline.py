# -------------------------
# IMPORTS
# -------------------------
# Core vector DB
import chromadb 

# Text splitting utility (for chunking documents)
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Vector store implementation (Chroma wrapper for LangChain)
from langchain_chroma import Chroma

# Document loaders for TXT and PDF
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PyPDFLoader
)

import glob

# Embedding model
from langchain_openai import OpenAIEmbeddings

# Tokenizer for chunk size calculation
import tiktoken

import os

# Load environment variables (API keys etc.)
from dotenv import load_dotenv
load_dotenv()

# Initialize Chroma client (disable telemetry)
client = chromadb.Client(settings=chromadb.Settings(anonymized_telemetry=False))
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import re


# -------------------------
# QUERY EXPANSION
# -------------------------
def expand_query(query):
    """
    Expands user query with related financial terms
    to improve retrieval quality.
    """
    q = query.lower()

    if "sip" in q:
        return query + " systematic investment plan mutual fund sip meaning definition monthly investment"

    # Add safe investment keywords
    if any(x in q for x in ["safe", "low risk", "secure"]):
        return query + " low risk investments bonds fixed deposits government securities treasury bills"

    # Add comparison keywords for equity vs debt
    if any(x in q for x in ["equity", "stock"]) and "debt" in q:
        return query + " difference between stocks and bonds risk return ownership fixed income"

    # Add bond duration explanation keywords
    if "duration" in q and "bond" in q:
        return query + " bond duration interest rate sensitivity definition meaning price change interest rates"

    return query


# -------------------------
# RERANKING FUNCTION
# -------------------------
def rerank(results, query):
    """
    Improves ranking by boosting results
    that contain more query word overlap.
    """
    q_words = query.lower().split()

    def score_boost(r):
        # Count how many query words appear in content
        overlap = sum(1 for w in q_words if w in r["content"].lower())

        # Slight boost for overlap
        return r["score"] + 0.05 * overlap

    # Sort descending based on boosted score
    return sorted(results, key=score_boost, reverse=True)


# -------------------------
# TEXT CLEANING
# -------------------------
def clean_text(text):
    """
    Cleans noisy PDF text:
    - Removes page numbers
    - Removes regulatory noise
    - Normalizes whitespace
    """
    if not text:   # Handles None or empty
        return ""

    text = text.replace("\n", " ").strip()

    # Remove page indicators
    text = re.sub(r'page\s*\d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d+\s*\|\s*page', '', text, flags=re.IGNORECASE)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove legal / regulatory noise patterns
    noise_patterns = [
        r'section\s+\d+(\(\w+\))?',
        r'clause\s+\d+',
        r'regulation\s+\d+',
        r'code\s+\d+'
    ]

    for pattern in noise_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    return text.strip()


# -------------------------
# USEFUL CONTENT FILTER
# -------------------------
def is_useful(text):
    """
    Filters out very small / meaningless chunks.
    """
    words = text.split()
    return len(words) > 20 


# -------------------------
# DEDUPLICATION
# -------------------------
def deduplicate(results):
    """
    Removes duplicate results based on source file name.
    Ensures diversity of documents.
    """
    seen = set()
    final = []

    for r in results:
        if r["source_file_name"] not in seen:
            final.append(r)
            seen.add(r["source_file_name"])

    return final


# -------------------------
# RAG PIPELINE CLASS
# -------------------------
class RAGPipeline:

    """
    RAGPipeline builds an end-to-end Retrieval-Augmented Generation system.

    Flow:
    1. Load documents from folder
    2. Split documents into smaller chunks
    3. Convert chunks into embeddings
    4. Store embeddings in a vector database (Chroma)
    5. Retrieve relevant chunks based on user query
    """

    def __init__(self):
        # Path where all input documents are stored
        self.folder_path = "data/financial_docs"

        # Step 1: Load documents
        self.documents = self.__load_documents()

        # Step 2: Split documents into chunks
        self.chunks = self.__split_documents(self.documents)

        # Step 3: Create / load vector DB
        self.vectorstore = self.__create_vector_store(self.chunks)

        # Step 4: Create retriever (top 3 results)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        

    def __load_documents(self):
        """
        Loads TXT and PDF documents from folder.
        Applies cleaning and filtering.
        """

        all_docs = []

        # -------------------------
        # LOAD TXT FILES
        # -------------------------
        txt_loader = DirectoryLoader(
            path=self.folder_path,
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            show_progress=True,
            use_multithreading=False   # Stability fix
        )
        all_docs.extend(txt_loader.load())
        
        # -------------------------
        # LOAD PDF FILES
        # -------------------------
        pdf_files = glob.glob(os.path.join(self.folder_path, "**/*.pdf"), recursive=True)
        
        for file in pdf_files:
            try:
                loader = PyPDFLoader(file)
                docs = loader.load()

                cleaned_docs = []

                for doc in docs:
                    # Clean text
                    text = clean_text(doc.page_content)

                    # Keep only useful content
                    if is_useful(text):
                        doc.page_content = text
                        cleaned_docs.append(doc)

                all_docs.extend(cleaned_docs)

            except Exception as e:
                print(f"Skipping {file}: {e}")

        # Safety check
        if not all_docs:
            raise ValueError(f"No documents found in {self.folder_path}")

        # -------------------------
        # ADD METADATA
        # -------------------------
        for doc in all_docs:
            source = doc.metadata.get("source", "")

            if source.endswith(".pdf"):
                doc.metadata["file_type"] = "pdf"
            elif source.endswith(".txt"):
                doc.metadata["file_type"] = "txt"

        return all_docs


    def __split_documents(self, docs: list) -> list:
        """
        Splits documents into smaller chunks using token-based splitting.
        """

        # Tokenizer aligned with OpenAI models
        encoding = tiktoken.get_encoding("cl100k_base")

        # Token length calculator
        def _token_length(text):
            return len(encoding.encode(text))

        # Recursive splitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,                 # Max tokens per chunk
            chunk_overlap=200,              # Overlap for context continuity
            length_function=_token_length,  # Token-based splitting
            separators=["\n\n", "\n", ".", " ", ""]  # Splitting priority
        )

        # Perform splitting
        chunks = splitter.split_documents(docs)

        return chunks


    def __create_vector_store(self, chunks: list):
        """
        Creates or loads Chroma vector database.
        """

        # Initialize embedding model
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            chunk_size=750,     # Batch size
            dimensions=1536,    # Embedding size
            max_retries=3       # Retry mechanism
        )

        # -------------------------
        # LOAD EXISTING DB
        # -------------------------
        try:
            vectorstore = Chroma(
                persist_directory="chroma_fin_db",
                embedding_function=embeddings,
                collection_name="financial_docs",
                client_settings=chromadb.Settings(anonymized_telemetry=False)
            )

            # Ensure DB is not empty
            if vectorstore._collection.count() == 0:
                raise ValueError("Empty DB")

        # -------------------------
        # CREATE NEW DB
        # -------------------------
        except:
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory="chroma_fin_db",
                collection_name="financial_docs"
            )

        return vectorstore
        

    def retrieve(self, query: str) -> list:
        """
        Retrieves top relevant chunks for a query.
        """

        # Expand query for better recall
        query = expand_query(query)

        # Perform similarity search
        results = self.vectorstore.similarity_search_with_score(query, k=5)
    
        seen_sources = set()
        formatted_results = []

        # -------------------------
        # FORMAT RESULTS
        # -------------------------
        for doc, score in results:
            source_path = doc.metadata.get("source", "unknown")

            # Extract file name only
            file_name = os.path.basename(source_path)
            seen_sources.add(file_name)
    
            # Convert distance score → similarity score
            similarity = 1 / (1 + score)
        
            formatted_results.append({
                "content": doc.page_content,
                "source_file_name": file_name,
                "file_type": doc.metadata.get("file_type", "unknown"),
                "score": round(similarity, 3),
                "confidence": round(similarity, 3)
            })

        # Rerank results
        reranked = rerank(formatted_results, query)

        # Remove duplicates
        reranked = deduplicate(reranked)

        # Return top 3 results
        return reranked[:3]