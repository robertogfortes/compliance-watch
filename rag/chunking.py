"""
Text chunking strategies for RAG document preparation.

Prefer chunk_by_section when documents have section headers.
Use chunk_by_char or chunk_by_sentence for unstructured prose.
"""
import re


def chunk_by_section(document_text: str) -> list[str]:
    """Split on markdown-style section headers (## )."""
    pattern = r"\n## "
    return re.split(pattern, document_text)


def chunk_by_char(text: str, chunk_size: int = 150, chunk_overlap: int = 20) -> list[str]:
    """Fixed-size character chunks with overlap."""
    chunks = []
    start_idx = 0
    while start_idx < len(text):
        end_idx = min(start_idx + chunk_size, len(text))
        chunks.append(text[start_idx:end_idx])
        start_idx = end_idx - chunk_overlap if end_idx < len(text) else len(text)
    return chunks


def chunk_by_sentence(
    text: str,
    max_sentences_per_chunk: int = 5,
    overlap_sentences: int = 1,
) -> list[str]:
    """Group sentences into chunks with a one-sentence overlap."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    start_idx = 0
    while start_idx < len(sentences):
        end_idx = min(start_idx + max_sentences_per_chunk, len(sentences))
        chunks.append(" ".join(sentences[start_idx:end_idx]))
        start_idx += max_sentences_per_chunk - overlap_sentences
        if start_idx < 0:
            start_idx = 0
    return chunks
