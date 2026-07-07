from rag.loader import load_pdf
from rag.splitter import split_text
from rag.vector_store import add_chunks

pdf_path = "data/insurance/griha-brochure-uid-7869-416415238450.pdf"

text = load_pdf(pdf_path)

chunks = split_text(text)

add_chunks(
    chunks
)

print("Indexed successfully")