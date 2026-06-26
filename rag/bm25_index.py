"""
BM25 lexical index for exact-term retrieval (contract numbers, supplier IDs).

Interface contract: add_document, search — same as VectorIndex, compatible with Retriever.
"""
import math
import re
from collections import Counter
from typing import Callable


class BM25Index:
    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
        tokenizer: Callable[[str], list[str]] | None = None,
    ):
        self.documents: list[dict] = []
        self._corpus_tokens: list[list[str]] = []
        self._doc_len: list[int] = []
        self._doc_freqs: list[Counter] = []
        self._df: dict[str, int] = {}
        self._idf: dict[str, float] = {}
        self.k1 = k1
        self.b = b
        self._tokenizer = tokenizer or self._default_tokenizer

    def _default_tokenizer(self, text: str) -> list[str]:
        return [t for t in re.split(r"\W+", text.lower()) if t]

    def add_document(self, document: dict) -> None:
        tokens = self._tokenizer(document["content"])
        self.documents.append(document)
        self._corpus_tokens.append(tokens)
        self._doc_len.append(len(tokens))

        freq = Counter(tokens)
        self._doc_freqs.append(freq)
        for term in freq:
            self._df[term] = self._df.get(term, 0) + 1

        self._recompute_idf()

    def _recompute_idf(self) -> None:
        n = len(self.documents)
        for term, df in self._df.items():
            self._idf[term] = math.log((n - df + 0.5) / (df + 0.5) + 1)

    def search(self, query_text: str, k: int = 1) -> list[tuple[dict, float]]:
        if not self.documents:
            return []

        query_tokens = self._tokenizer(query_text)
        avg_len = sum(self._doc_len) / len(self._doc_len)
        scores: list[tuple[float, dict]] = []

        for idx, (doc, doc_freq, doc_len) in enumerate(
            zip(self.documents, self._doc_freqs, self._doc_len)
        ):
            score = 0.0
            for term in query_tokens:
                if term not in doc_freq:
                    continue
                tf = doc_freq[term]
                idf = self._idf.get(term, 0.0)
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * doc_len / avg_len)
                score += idf * (numerator / denominator)
            scores.append((score, doc))

        scores.sort(key=lambda x: x[0], reverse=True)
        return [(doc, score) for score, doc in scores[:k]]
