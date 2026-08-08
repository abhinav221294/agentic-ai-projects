import logging

from src.embeddings.providers.gemini_provider import (
    GeminiEmbeddingProvider,
)
# from src.embeddings.providers.sentence_transformer_provider import (
#     SentenceTransformerProvider,
# )

logger = logging.getLogger(__name__)


class EmbeddingService:

    def __init__(self):
        self.primary = GeminiEmbeddingProvider()
        # self.fallback = SentenceTransformerProvider()

    def embed(
        self,
        text: str,
    ) -> list[float]:

        try:
            return self.primary.embed(text)

        except Exception as e:

            logger.warning(
                f"Primary embedding provider failed: {e}"
            )

            raise

    def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        try:
            return self.primary.embed_batch(texts)

        except Exception as e:

            logger.warning(
                f"Primary embedding provider failed: {e}"
            )

            raise