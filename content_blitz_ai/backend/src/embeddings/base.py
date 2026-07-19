from abc import ABC, abstractmethod

class BaseEmbeddingProvider(ABC):

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Generate an embedding for a single piece of text."""
        pass

    @abstractmethod
    def embed_batch(self,
        texts: list[str],
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        pass

    