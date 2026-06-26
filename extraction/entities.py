"""
Extract structured entities from a document using prefill + stop sequence.

Returns a typed dict: {type, supplier, value, date, items, document_number}.
Never use thinking=True here — incompatible with prefill.
"""
import json
from typing import TypedDict

from core.claude_client import add_assistant_message, add_user_message, chat
from extraction.pdf_reader import load_pdf_document
from config import DEFAULT_MODEL, MAX_ANALYSIS_TEMPERATURE

_EXTRACTION_PROMPT = """Extract the key compliance fields from the document above.

Return a JSON object with exactly these fields:
- "type": one of "invoice", "contract", or "addendum"
- "supplier": supplier or counterpart name (string)
- "value": total monetary value as a number (float), or null if not found
- "currency": currency code, e.g. "BRL", "USD" (string or null)
- "date": issue date in ISO 8601 format YYYY-MM-DD (string or null)
- "document_number": document reference or number (string or null)
- "items": array of objects {description: string, value: float|null}, or []

Use null for any field not found in the document. Do not invent values."""


class DocumentEntities(TypedDict):
    type: str
    supplier: str
    value: float | None
    currency: str | None
    date: str | None
    document_number: str | None
    items: list[dict]


def extract_entities_from_pdf(pdf_path: str, title: str | None = None) -> DocumentEntities:
    """
    Extract structured entities from a PDF using prefill + stop sequence.
    """
    doc_block = load_pdf_document(pdf_path, title=title)

    messages = []
    add_user_message(messages, [doc_block, {"type": "text", "text": _EXTRACTION_PROMPT}])

    # Prefill forces JSON output; stop sequence closes the block cleanly
    add_assistant_message(messages, "```json")
    response = chat(
        messages,
        model=DEFAULT_MODEL,
        temperature=MAX_ANALYSIS_TEMPERATURE,
        stop_sequences=["```"],
    )

    raw = response.content[0].text if hasattr(response.content[0], "text") else str(response.content[0])
    return json.loads(raw.strip())


def extract_entities_from_text(document_text: str) -> DocumentEntities:
    """
    Extract structured entities from raw text (e.g., from scanned page analysis).
    """
    prompt = f"""<document>\n{document_text}\n</document>\n\n{_EXTRACTION_PROMPT}"""

    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```json")
    response = chat(
        messages,
        model=DEFAULT_MODEL,
        temperature=MAX_ANALYSIS_TEMPERATURE,
        stop_sequences=["```"],
    )

    raw = response.content[0].text if hasattr(response.content[0], "text") else str(response.content[0])
    return json.loads(raw.strip())
