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
from langchain_openai import OpenAIEmbeddings
#from tiktoken import encoding_for_model
import tiktoken
import os
# from langchain.schema import Document
from dotenv import load_dotenv
load_dotenv()
os.environ["ANONYMIZED_TELEMETRY"] = "False"


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

        # ---------------- TXT ----------------
        txt_loader = DirectoryLoader(
        path=self.folder_path,
        glob="*.txt",
        loader_cls=TextLoader,
        show_progress=True,
        use_multithreading=True
        )
        all_docs.extend(txt_loader.load())

        # ---------------- PDF ----------------
        pdf_loader = DirectoryLoader(
        path=self.folder_path,
        glob="*.pdf",
        loader_cls=PyPDFLoader,
        show_progress=True,
        use_multithreading=True
        )
        all_docs.extend(pdf_loader.load())

        # ✅ Add metadata (VERY IMPORTANT)
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
            chunk_overlap=150,               # Overlap to preserve context
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
            dimensions=1024,     # Reduced dimension for faster retrieval
            max_retries=3        # Retry mechanism for API failures
        )

        # Check if vector DB already exists
        if os.path.exists("chroma_fin_db") and os.listdir("chroma_fin_db"):
            # Load existing vector store (avoids recomputation)
            vectorstore = Chroma(
                persist_directory="chroma_fin_db",
                embedding_function=embeddings,
                collection_name="financial_docs"
            )
        else:
            # Create new vector store from documents
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

        # Perform similarity search with relevance scores
        results = self.vectorstore.similarity_search_with_score(query, k=3)

        # Track unique sources to avoid duplicate display
        seen_sources = set()

        formatted_results = []

        # Process retrieved results
        for doc, score in results:
            # Extract source path from metadata
            source_path = doc.metadata.get("source", "unknown")

            # Extract only file name for user-friendly display
            file_name = os.path.basename(source_path)

            # Skip duplicate sources (UX improvement)
            if file_name in seen_sources:
                continue

            seen_sources.add(file_name)
    
           
            # Format output
            formatted_results.append({
            "content": doc.page_content,
            "source_file_name": file_name,
            "file_type": doc.metadata.get("file_type", "unknown"),
            "score": round(score, 3),
            })

        return formatted_results