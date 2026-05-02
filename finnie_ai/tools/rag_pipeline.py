from langchain_text_splitters import RecursiveCharacterTextSplitter
#from langchain.vectorstores import Chroma
#from langchain.embeddings.openai import OpenAIEmbeddings
#from langchain.document_loaders import DirectoryLoader, TextLoader
#from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PyPDFLoader
)
import glob
from langchain_openai import OpenAIEmbeddings
#from tiktoken import encoding_for_model
import tiktoken
import os
# from langchain.schema import Document
from dotenv import load_dotenv
load_dotenv()
os.environ["ANONYMIZED_TELEMETRY"] = "False"
import re

def expand_query(query):
    q = query.lower()

    if any(x in q for x in ["safe", "low risk", "secure"]):
        return query + " low risk investments bonds fixed deposits government securities treasury bills"

    if any(x in q for x in ["equity", "stock"]) and "debt" in q:
        return query + " difference between stocks and bonds risk return ownership fixed income"

    if "duration" in q and "bond" in q:
        return query + " bond duration interest rate sensitivity definition meaning price change interest rates"
    return query

def rerank(results, query):
    q_words = query.lower().split()

    def score_boost(r):
        overlap = sum(1 for w in q_words if w in r["content"].lower())
        return r["score"] + 0.05 * overlap

    return sorted(results, key=score_boost, reverse=True)


def clean_text(text):
    if not text:   # ✅ handles None or empty
        return ""

    text = text.replace("\n", " ").strip()

    text = re.sub(r'page\s*\d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d+\s*\|\s*page', '', text, flags=re.IGNORECASE)

    text = re.sub(r'\s+', ' ', text)

    noise_patterns = [
        r'section\s+\d+(\(\w+\))?',
        r'clause\s+\d+',
        r'regulation\s+\d+',
        r'code\s+\d+'
    ]

    for pattern in noise_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    return text.strip()

def is_useful(text):
    words = text.split()
    return len(words) > 20 

def deduplicate(results):
    seen = set()
    final = []

    for r in results:
        if r["source_file_name"] not in seen:
            final.append(r)
            seen.add(r["source_file_name"])

    return final

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
        # Path where all input documents (.txt files) are stored
        self.folder_path = "data/financial_docs"

        # Step 1: Load documents from folder
        self.documents = self.__load_documents()

        # Step 2: Split documents into smaller chunks for better retrieval
        self.chunks = self.__split_documents(self.documents)

        # Step 3: Create vector database (embeddings + storage)
        self.vectorstore = self.__create_vector_store(self.chunks)

        # Step 4: Create retriever object with top-k control
        # This retriever will fetch top 5 most relevant chunks
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        

    def __load_documents(self):

        all_docs = []

        ## TXT
        txt_loader = DirectoryLoader(
        path=self.folder_path,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
        use_multithreading=False   # ✅ fixed
        )
        all_docs.extend(txt_loader.load())
        
        # PDF (safe loading)
        pdf_files = glob.glob(os.path.join(self.folder_path, "**/*.pdf"), recursive=True)
        
        for file in pdf_files:
            try:
                loader = PyPDFLoader(file)
                docs = loader.load()
                cleaned_docs = []
                for doc in docs:
                    text = clean_text(doc.page_content)
                    if is_useful(text):
                        doc.page_content = text
                        cleaned_docs.append(doc)
                all_docs.extend(cleaned_docs)
            except Exception as e:
                print(f"Skipping {file}: {e}")

        if not all_docs:
            raise ValueError(f"No documents found in {self.folder_path}")

        # metadata
        for doc in all_docs:
            source = doc.metadata.get("source", "")

            if source.endswith(".pdf"):
                doc.metadata["file_type"] = "pdf"
            elif source.endswith(".txt"):
                doc.metadata["file_type"] = "txt"

        return all_docs

    def __split_documents(self, docs: list) -> list:
        """
        Splits large documents into smaller chunks.

        Why splitting is important:
        - LLMs have token limits
        - Smaller chunks improve retrieval accuracy
        - Helps maintain semantic context

        Args:
            docs (list): List of Document objects

        Returns:
            list[Document]: Chunked documents
        """

        # Create tokenizer aligned with GPT-4
        # This ensures chunk size is measured in tokens (not characters)
        #encoding = tiktoken.encoding_for_model("gpt-4")
        encoding = tiktoken.get_encoding("cl100k_base")

        # Custom function to calculate token length of text
        def _token_length(text):
            return len(encoding.encode(text))

        # RecursiveCharacterTextSplitter:
        # - Splits text hierarchically:
        #   paragraphs → lines → words → characters
        # - Maintains semantic structure as much as possible
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,                 # Max tokens per chunk
            chunk_overlap=200,               # Overlap to preserve context
            length_function=_token_length,   # Use token-based length
            separators=["\n\n", "\n", ".", " ", ""]  # Priority splitting strategy
        )

        # Perform splitting
        chunks = splitter.split_documents(docs)
        
        
        # For checking chunk size
        #print(len(chunks))


        return chunks


    def __create_vector_store(self, chunks: list):
        """
        Creates or loads a vector database using Chroma.

        Steps:
        - Convert chunks into embeddings
        - Store embeddings in Chroma DB
        - Persist data for reuse

        Args:
            chunks (list): List of chunked Document objects

        Returns:
            Chroma: Vector store instance
        """

        # Initialize embedding model
        # Using small model for cost + speed optimization
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            chunk_size=750,     # Batch size for embedding requests
            dimensions=1536,     # Reduced dimension for faster retrieval
            max_retries=3        # Retry mechanism for API failures
        )

        # Check if vector DB already exists
        try:
            vectorstore = Chroma(
                persist_directory="chroma_fin_db",
                embedding_function=embeddings,
                collection_name="financial_docs"
                )

            # sanity check
            if vectorstore._collection.count() == 0:
                raise ValueError("Empty DB")

        except:
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory="chroma_fin_db",
                collection_name="financial_docs"
                )
            # Persist to disk for future use
            #vectorstore.persist()

        return vectorstore
        

    def retrieve(self, query: str) -> list:
        """
        Retrieves top relevant chunks for a given query.

        Features:
        - Semantic similarity search
        - Score-based ranking
        - Source attribution
        - Deduplication of sources

        Args:
            query (str): User query

        Returns:
            list[dict]: List of results with content, source, and score
        """

        query = expand_query(query)
        # Perform similarity search with relevance scores
        results = self.vectorstore.similarity_search_with_score(query, k=5)
    
        # Track unique sources to avoid duplicate display
        seen_sources = set()

        formatted_results = []

        # Process retrieved results
        for doc, score in results:
            # Extract source path from metadata
            source_path = doc.metadata.get("source", "unknown")

            # Extract only file name for user-friendly display
            file_name = os.path.basename(source_path)
            seen_sources.add(file_name)
    
            similarity = 1 / (1 + score)
        
            # Format output
            formatted_results.append({
            "content": doc.page_content,
            "source_file_name": file_name,
            "file_type": doc.metadata.get("file_type", "unknown"),
            "score": round(similarity, 3),
            "confidence": round(similarity, 3)
            })
        reranked = rerank(formatted_results, query)
        reranked = deduplicate(reranked)
        return reranked[:3]