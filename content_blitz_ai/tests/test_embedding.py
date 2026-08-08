from src.embeddings.providers.gemini_provider import GeminiEmbeddingProvider

provider = GeminiEmbeddingProvider()

embedding = provider.embed("Hello world")

print("Embedding dimension:", len(embedding))
print("First 5 values:", embedding[:5])