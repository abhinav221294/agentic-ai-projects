from rag.loader import load_pdf
from rag.splitter import split_text
from rag.vector_store import add_chunks


def ingest_document(pdf_path):

    text = load_pdf(pdf_path)

    chunks = split_text(text)

    add_chunks(chunks)

    print(f"Indexed {len(chunks)} chunks successfully.")