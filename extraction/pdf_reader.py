"""
Read a PDF file and return a Claude document block with citations enabled.

Every call that analyses a document MUST use this module — citations.enabled=True
is a hard architectural requirement, not optional.
"""
import base64
from pathlib import Path


def load_pdf_document(pdf_path: str | Path, title: str | None = None) -> dict:
    """
    Load a PDF file and return a Claude document block ready for message content.

    The returned block has citations.enabled=True so every claim Claude makes
    about the document can be traced back to the exact source excerpt.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file, got: {path.suffix}")

    raw_bytes = path.read_bytes()
    encoded = base64.standard_b64encode(raw_bytes).decode("utf-8")

    return {
        "type": "document",
        "source": {
            "type": "base64",
            "media_type": "application/pdf",
            "data": encoded,
        },
        "title": title or path.name,
        "citations": {"enabled": True},
    }


def load_pdf_bytes(pdf_bytes: bytes, title: str) -> dict:
    """Same as load_pdf_document but accepts raw bytes (e.g., from an upload)."""
    if not pdf_bytes:
        raise ValueError("pdf_bytes cannot be empty")
    encoded = base64.standard_b64encode(pdf_bytes).decode("utf-8")
    return {
        "type": "document",
        "source": {
            "type": "base64",
            "media_type": "application/pdf",
            "data": encoded,
        },
        "title": title,
        "citations": {"enabled": True},
    }
