"""
This file contains the HybridSearcher class that is to improve the search result accuracy for RAG.
"""

from .embedding import Embedder
from .db_setup import VectorDatabaseSetup
from .keyword_engine import KeywordEngine
from .config import PERSIST_DIR


class HybridSearcher:
    """
    Uses ChromaDB vector search to get a candidate pool, then re-ranks
    that pool using BM25 keyword search for more precise retrieval.
    """

    def __init__(self, embedder: Embedder, db: VectorDatabaseSetup):
        self.embedder = embedder
        self.db = db

    def search(self, query: str, n_results: int = 3, candidate_pool: int = 20):
        """
        1. Vector search to get `candidate_pool` semantically similar chunks.
        2. BM25 keyword re-rank those chunks.
        3. Return top `n_results`.

        Args:
            query:          The search query string.
            n_results:      Final number of results to return.
            candidate_pool: How many candidates to fetch from Chroma before re-ranking.
                            Should be larger than n_results (e.g. 20 for top 3 final results).
        """
        print(f"\n--- Running Hybrid Search for: '{query}' ---")

        # 1. --- VECTOR SEARCH (Semantic) ---
        # Fetch a larger candidate pool from Chroma
        query_vector = self.embedder.get_batch_embeddings([query])
        vector_data = self.db.query_vectors(
            query_embeddings=query_vector, n_results=candidate_pool
        )

        candidate_ids = vector_data["ids"][0]  # e.g. 20 IDs
        candidate_docs = vector_data["documents"][0]  # matching texts

        if not candidate_docs:
            print("No candidates returned from vector search.")
            return {"ids": [], "documents": []}

        print(
            f"Vector search returned {len(candidate_docs)} candidates for re-ranking."
        )

        # 2. --- KEYWORD RE-RANK on the candidate pool only ---
        # Build a fresh BM25 index on just these candidates (small, fast)
        keyword_engine = KeywordEngine(documents=candidate_docs, ids=candidate_ids)
        keyword_results = keyword_engine.search(query=query, n_results=n_results)

        # 3. --- FETCH & RETURN final top-N docs ---
        final_ids = [res["id"] for res in keyword_results]

        final_documents = self.db.collection.get(ids=final_ids, include=["documents"])

        # Print results
        for i, (doc_id, text) in enumerate(
            zip(final_documents["ids"], final_documents["documents"])
        ):
            print(f"Rank {i+1} (ID: {doc_id[:8]}...): {text[:120]}...")

        return final_documents


# --- How to run it ---
if __name__ == "__main__":
    my_embedder = Embedder()
    my_db = VectorDatabaseSetup(persist_directory=PERSIST_DIR)

    hybrid = HybridSearcher(embedder=my_embedder, db=my_db)

    # Try a query where a keyword might matter more than pure semantics
    TEST_CASE = """
        I am a fresh grad who just started working, and i would like to buy a house. What schemes
        can be helpful to me and my girlfriend?
    """
    results = hybrid.search(TEST_CASE)
    print(type(results))
