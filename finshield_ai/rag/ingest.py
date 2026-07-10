from rag.loader import load_pdf
from rag.splitter import split_text
from rag.vector_store import add_chunks


def ingest_document(pdf_path):

    text = load_pdf(pdf_path)

    if not text.strip():
        raise ValueError(
            "No extractable text found in the PDF. "
            "This PDF appears to be scanned or image-based."
        )

    chunks = split_text(text)

    if not chunks:
        raise ValueError("No chunks could be generated from the document.")

    add_chunks(chunks)