"""
Analyse scanned document pages (images) using Claude's vision capability.

Structured step-by-step prompt ensures consistent extraction even from low-quality scans.
"""
import base64
from pathlib import Path

from core.claude_client import add_user_message, chat, text_from_message
from config import DEFAULT_MODEL, MAX_ANALYSIS_TEMPERATURE

_SUPPORTED_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}

_SCAN_PROMPT = """You are analysing a scanned page from a financial document.
Follow these steps in order:

<steps>
1. Identify the document type: invoice, contract, or addendum.
2. Locate and extract the document number or reference code.
3. Locate and extract the supplier / counterpart name.
4. Locate and extract the total monetary value and currency.
5. Locate and extract the issue date.
6. List any line items visible on the page (description + value), or state "none visible".
7. Note any compliance-relevant clauses, seals, or signatures visible.
</steps>

Return your findings as plain text, one section per step.
Use only information visible in the image — do not infer or fabricate."""


def analyse_scanned_page(image_path: str | Path) -> str:
    """
    Send a scanned page image to Claude and return structured extraction text.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    media_type = _SUPPORTED_TYPES.get(path.suffix.lower())
    if not media_type:
        raise ValueError(f"Unsupported image type: {path.suffix}. Supported: {list(_SUPPORTED_TYPES)}")

    encoded = base64.standard_b64encode(path.read_bytes()).decode("utf-8")

    messages = []
    add_user_message(messages, [
        {
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": encoded},
        },
        {"type": "text", "text": _SCAN_PROMPT},
    ])

    response = chat(messages, model=DEFAULT_MODEL, temperature=MAX_ANALYSIS_TEMPERATURE)
    return text_from_message(response)
