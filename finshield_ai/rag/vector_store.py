import chromadb

from rag.embeddings import get_embedding_model

model = get_embedding_model()

client = chromadb.PersistentClient(
    path=".chromadb"
)

collection = client.get_or_create_collection(
    "finshield"
)


def add_chunks(chunks):

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

        n_results=3

    )

    return results