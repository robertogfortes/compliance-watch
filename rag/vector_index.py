"""
In-memory vector index with cosine distance search.

Interface contract: add_vector, add_document, search.
Compatible with Retriever (rag/retriever.py) — do not change the method signatures.
"""
import math
from typing import Callable


class VectorIndex:
    def __init__(
        self,
        distance_metric: str = "cosine",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ):
        self.vectors: list[list[float]] = []
        self.documents: list[dict] = []
        self._vector_dim: int | None = None
        self._distance_metric = distance_metric
        self._embedding_fn = embedding_fn

    def add_vector(self, vector: list[float], document: dict) -> None:
        self.vectors.append(list(vector))
        self.documents.append(document)
        if self._vector_dim is None:
            self._vector_dim = len(vector)

    def add_document(self, document: dict) -> None:
        if self._embedding_fn is None:
            raise RuntimeError("embedding_fn required to call add_document")
        vector = self._embedding_fn(document["content"])
        self.add_vector(vector, document)

    def search(self, query: str | list[float], k: int = 1) -> list[tuple[dict, float]]:
        if not self.vectors:
            return []
        query_vector = self._embedding_fn(query) if isinstance(query, str) else query
        distances = [
            (self._cosine_distance(query_vector, v), doc)
            for v, doc in zip(self.vectors, self.documents)
        ]
        distances.sort(key=lambda item: item[0])
        return [(doc, dist) for dist, doc in distances[:k]]

    def _cosine_distance(self, vec1: list[float], vec2: list[float]) -> float:
        dot = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))
        if mag1 == 0 or mag2 == 0:
            return 1.0
        similarity = max(-1.0, min(1.0, dot / (mag1 * mag2)))
        return 1.0 - similarity
