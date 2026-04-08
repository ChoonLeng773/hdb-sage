"""
Vector database setup and management for ChromaDB.

Intended for use in embedding pipelines where documents are
split into vectors for retrieval or search applications.
"""

# import numpy as np
import chromadb

from .config import CHROMA_COLLECTION_NAME, NUM_QUERY_RESULTS


class VectorDatabaseSetup:
    """
    Wrapper for managing a local Chroma vector database collection.

    This class handles:
    - Connecting to a persistent Chroma database.
    - Creating or fetching a collection (idempotent).
    - Upserting vectors with associated document texts and metadata.

    Attributes:
        client (chromadb.PersistentClient): Chroma client connected to the specified path.
        collection_name (str): Name of the collection in the database.
        collection (chromadb.Collection): The Chroma collection object.
    """

    def __init__(
        self,
        persist_directory: str,  # required fields to prevent misbehaviouur
        collection_name: str = CHROMA_COLLECTION_NAME,
        reset_db: bool = False,  # 👈 add this flag
    ):
        """Connect to local Chroma DB and ensure the collection exists."""
        print(f"Connecting to Chroma DB at {persist_directory}...")
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = collection_name

        if reset_db:
            try:
                print(f"Resetting collection '{collection_name}'...")
                self.client.delete_collection(name=collection_name)
            except Exception:
                # Collection may not exist yet → ignore
                print("No existing collection to delete.")

        # get_or_create_collection is idempotent
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

    def upsert_vectors(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ):
        """Insert data into Chroma. It requires separate lists for each field."""
        print(
            f"Inserting {len(ids)} records into Chroma collection '{self.collection_name}'..."
        )
        # type safe warning
        # allowed_types = (str, int, float, bool, type(None))
        # safe_metadatas = []
        # for md in metadatas:
        #     safe_md = {k: v for k, v in md.items() if isinstance(v, allowed_types)}
        #     safe_metadatas.append(safe_md)
        # np type -> for type safe linting
        # embeddings_np = np.array(embeddings, dtype=np.float32)
        # Changed .add() to .upsert() to prevent adding to an ID that already exists
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def get_all_documents(self):
        """Fetches all IDs and text documents from Chroma to build the keyword index."""
        # Note: In massive databases, you'd want to paginate this.
        results = self.collection.get(include=["documents"])
        return results["ids"], results["documents"]

    def query_vectors(
        self, query_embeddings: list[list[float]], n_results: int = NUM_QUERY_RESULTS
    ):
        """Search the database for the closest vectors. -> updated to hybrid search"""
        # query_np = np.array(query_embeddings, dtype=np.float32)
        results = self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            include=["documents", "embeddings", "metadatas"],
        )
        return results
