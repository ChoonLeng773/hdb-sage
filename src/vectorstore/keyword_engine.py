from rank_bm25 import BM25Okapi


class KeywordEngine:
    def __init__(self, documents: list[str], ids: list[str]):
        """
        Initializes the BM25 keyword search index.
        In a real production app, you would save/load this index to a file,
        but for simplicity, we build it in-memory here.
        """
        print("Building BM25 Keyword Index...")
        self.ids = ids
        self.documents = documents

        # BM25 requires text to be tokenized (split into words)
        tokenized_corpus = [self._tokenize(doc) for doc in documents]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def _tokenize(self, text: str) -> list[str]:
        """A simple tokenizer. Converts to lowercase and splits by space."""
        return text.lower().split(" ")

    def search(self, query: str, n_results: int = 5) -> list[dict]:
        """Searches the keyword index and returns the top IDs and their scores."""
        tokenized_query = self._tokenize(query)

        # Get raw scores for all documents
        scores = self.bm25.get_scores(tokenized_query)

        # Pair IDs with scores, sort descending, and grab the top N
        id_scores = list(zip(self.ids, scores))
        id_scores.sort(key=lambda x: x[1], reverse=True)

        return [{"id": item[0], "score": item[1]} for item in id_scores[:n_results]]
