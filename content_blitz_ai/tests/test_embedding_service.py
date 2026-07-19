from src.embeddings.embedding_service import EmbeddingService


def test_embed_returns_embedding():
    service = EmbeddingService()

    embedding = service.embed(
        "Artificial Intelligence is transforming healthcare."
    )

    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert isinstance(embedding[0], float)