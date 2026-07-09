import chromadb

from rag.embeddings import get_embedding_model
from app.config import CHROMADB_PATH,TOP_K  

model = get_embedding_model()

client = chromadb.PersistentClient(
    path=CHROMADB_PATH
)

collection = client.get_or_create_collection(
    "finshield"
)


def add_chunks(chunks):

    # Clear previous document
    existing = collection.get()

    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    vectors = model.encode(chunks)

    collection.add(
        documents=chunks,
        embeddings=vectors.tolist(),
        ids=[str(i) for i in range(len(chunks))]
    )


def retrieve(query):

    q = model.encode([query])

    results = collection.query(
        query_embeddings=q.tolist(),
        n_results=TOP_K
    )

    return results