# import uuid
import hashlib
from pathlib import Path

from embedding import Embedder
from db_setup import VectorDatabaseSetup
from config import PERSIST_DIR, CHUNKS_DIR
from load_data import load_json_chunks


class DatabasePopulator:
    """
    Handles the processing and ingestion of raw documents into a vector database.

    This class is responsible for:
    - Extracting text from raw document inputs
    - Generating embeddings using the provided embedding model
    - Creating stable, deterministic IDs for each text chunk
    - Formatting metadata for storage
    - Uploading data to a vector database in batches
    """

    def __init__(self, embedder: Embedder, db: VectorDatabaseSetup):
        self.embedder = embedder
        self.db = db

    def process_and_upload(self, raw_documents: list[dict], batch_size: int = 100):
        """Processes raw text and uploads to Chroma in batches."""
        for i in range(0, len(raw_documents), batch_size):
            batch = raw_documents[i : i + batch_size]

            # 1. Extract text and generate embeddings
            texts = [doc["text"] for doc in batch]
            embeddings = self.embedder.get_batch_embeddings(texts)

            # 2. Format parallel lists for Chroma
            # ids = [str(uuid.uuid4()) for doc in batch]
            # INSTEAD OF UUIDs, USE FILE HASH FROM THE TEXT
            ids = [hashlib.md5(text.encode("utf-8")).hexdigest() for text in texts]
            metadatas = [
                {"source": doc.get("source", "unknown")} for doc in batch
            ]  # change this

            # 3. Upload the batch
            self.db.upsert_vectors(
                ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas
            )

        print("Vector database successfully populated!")


def run():
    # 1. Load data
    raw_data = load_json_chunks(CHUNKS_DIR)
    # 2. Initialize local services
    my_embedder = Embedder()  # Defaults to all-MiniLM-L6-v2
    persist_path = Path(__file__).resolve().parents[2] / PERSIST_DIR
    my_db = VectorDatabaseSetup(persist_directory=str(persist_path))

    # 3. Start orchestrator
    populator = DatabasePopulator(embedder=my_embedder, db=my_db)

    # 4. Run data uploading
    populator.process_and_upload(raw_data)


if __name__ == "__main__":
    run()
