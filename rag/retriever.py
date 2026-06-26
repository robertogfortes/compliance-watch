"""
Hybrid retriever combining any number of indexes via Reciprocal Rank Fusion.

Accepts VectorIndex, BM25Index, or any object exposing add_document and search(query, k).
"""


class Retriever:
    def __init__(self, *indexes):
        if len(indexes) == 0:
            raise ValueError("At least one index must be provided")
        self._indexes = list(indexes)

    def add_document(self, document: dict) -> None:
        for index in self._indexes:
            index.add_document(document)

    def search(self, query_text: str, k: int = 1, k_rrf: int = 60) -> list[tuple[dict, float]]:
        all_results = [index.search(query_text, k=k * 2) for index in self._indexes]

        scores: dict[str, dict] = {}
        for results in all_results:
            for rank, (doc, _) in enumerate(results, start=1):
                key = doc["content"]
                if key not in scores:
                    scores[key] = {"doc": doc, "score": 0.0}
                scores[key]["score"] += 1.0 / (k_rrf + rank)

        ranked = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
        return [(item["doc"], item["score"]) for item in ranked[:k]]
