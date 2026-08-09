from google import genai

from src.embeddings.base import BaseEmbeddingProvider
from src.core.config import GOOGLE_API_KEY,EMBEDDING_MODEL, VECTOR_DIMENSION


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    
    def __init__(self):
        self.client = genai.Client(
            api_key = GOOGLE_API_KEY
        )

        self.model = EMBEDDING_MODEL
    
    def embed(
        self,
        text: str
        ) -> list[float]:
        response = self.client.models.embed_content(
            model=self.model,
            contents=text,
             config={
                "output_dimensionality": VECTOR_DIMENSION
                }
        )

        return response.embeddings[0].values

    def embed_batch(
        self,
        texts: list[str]
    ) -> list[list[float]]:
        response = self.client.models.embed_content(
            model=self.model,
            contents=texts,
            config={
            "output_dimensionality": VECTOR_DIMENSION
            }
        )

        return [
            embedding.values
            for embedding in response.embeddings
        ]