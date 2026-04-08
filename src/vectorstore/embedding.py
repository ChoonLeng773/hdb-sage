from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL


class Embedder:

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """Initialize the local Hugging Face model."""
        print(f"Loading local embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)

    def get_embedding(self, text: str) -> list[float]:
        """Convert a single string into a vector."""
        return self.model.encode(text).tolist()

    def get_batch_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Convert a list of strings into vectors.
        sentence-transformers is highly optimized for batching.
        """
        return self.model.encode(texts).tolist()
