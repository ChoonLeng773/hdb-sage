"""
This file contains the HybridSearcher class that is to improve the search result accuracy for RAG.
"""

from .embedding import Embedder
from .db_setup import VectorDatabaseSetup
from .keyword_engine import KeywordEngine
from .config import PERSIST_DIR


class HybridSearcher:
    """
    This class contains the functionality to look for the most relevant chunks using hybrid search
    which involves both cosine similarity and keyword matching to create a better ranking for
    retrieval
    """

    def __init__(self, embedder: Embedder, db: VectorDatabaseSetup):
        self.embedder = embedder
        self.db = db

        # Fetch all documents from Chroma to fuel our Keyword Engine
        ids, documents = self.db.get_all_documents()
        self.keyword_engine = KeywordEngine(documents=documents, ids=ids)

    def reciprocal_rank_fusion(
        self, vector_results: list[str], keyword_results: list[str], k: int = 60
    ) -> list[str]:
        """
        Combines two ranked lists of IDs.
        Formula: 1 / (k + rank). Items appearing high on BOTH lists get a massive boost.
        """
        rrf_scores = {}

        # Process Vector Results
        for rank, doc_id in enumerate(vector_results):
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = 0
            rrf_scores[doc_id] += 1 / (k + rank + 1)  # +1 so rank starts at 1, not 0

        # Process Keyword Results
        for rank, doc_id in enumerate(keyword_results):
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = 0
            rrf_scores[doc_id] += 1 / (k + rank + 1)

        # Sort by the new fused score
        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        # Return just the ordered IDs
        return [item[0] for item in sorted_results]

    def search(self, query: str, n_results: int = 3):
        """Performs both searches and fuses the results."""
        print(f"\n--- Running Hybrid Search for: '{query}' ---")

        # 1. --- VECTOR SEARCH (Semantic) ---
        query_vector = self.embedder.get_batch_embeddings([query])
        vector_data = self.db.query_vectors(
            query_embeddings=query_vector, n_results=n_results
        )
        # Extract just the IDs from Chroma's result format
        vector_ranked_ids = vector_data["ids"][0]

        # 2. --- KEYWORD SEARCH (Exact Matches) ---
        keyword_data = self.keyword_engine.search(query=query, n_results=n_results)
        # Extract just the IDs
        keyword_ranked_ids = [res["id"] for res in keyword_data]

        # 3. --- FUSE THE RESULTS ---
        final_ranked_ids = self.reciprocal_rank_fusion(
            vector_ranked_ids, keyword_ranked_ids
        )

        # 4. Fetch the actual text for the winning IDs to display them
        final_documents = self.db.collection.get(
            ids=final_ranked_ids[:n_results], include=["documents"]
        )

        # Print results
        for i, (doc_id, text) in enumerate(
            zip(final_documents["ids"], final_documents["documents"])
        ):
            print(f"Rank {i+1} (ID: {doc_id[:8]}...): {text}")

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
