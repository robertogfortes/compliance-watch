"""
VoyageAI text embeddings using voyage-3-large.

Returns a list[float] vector for a given text string.
"""
import voyageai

from config import VOYAGE_API_KEY

_client = voyageai.Client(api_key=VOYAGE_API_KEY)
_MODEL = "voyage-3-large"


def embed(text: str) -> list[float]:
    """Embed a single text string and return its vector."""
    if not text or not text.strip():
        raise ValueError("text cannot be empty")
    result = _client.embed([text], model=_MODEL)
    return result.embeddings[0]


def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed multiple texts in a single API call (more efficient than looping)."""
    if not texts:
        raise ValueError("texts list cannot be empty")
    result = _client.embed(texts, model=_MODEL)
    return result.embeddings
