"""
MCP resource definitions — expose documents list and individual document content.

Resources allow @mention in Claude's UI so analysts can reference a document directly.
"""
from mcp_server.server import mcp

_DOCUMENTS: dict[str, str] = {
    "INV-SYN-2024-001": (
        "INVOICE — Synthex Supplies Ltda\n"
        "Date: 2024-03-15 | Total: BRL 17,300.00\n"
        "Items: Office equipment maintenance (BRL 4,500) + Network infrastructure upgrade (BRL 12,800)"
    ),
    "NF-NEX-2024-0042": (
        "NOTA FISCAL — Nexoria Consulting S.A.\n"
        "Date: 2024-04-02 | Total: BRL 34,000.00\n"
        "Items: Compliance consulting (BRL 28,000) + Contract review 20h (BRL 6,000)"
    ),
    "CTR-VLT-2024-007": (
        "CONTRACT — Veltron Technology Partners\n"
        "Effective: 2024-01-10 | Expiry: 2024-12-31 | Annual value: BRL 96,000.00\n"
        "Scope: Annual software licensing and support for internal ERP modules"
    ),
    "ADD-AUR-2024-002": (
        "ADDENDUM — Auramid Facilities Ltda\n"
        "Original contract: CTR-AUR-2023-015 | Date: 2024-05-20\n"
        "Reason: Extension to Building C | Value adjustment: +BRL 3,200/month"
    ),
    "INV-CRT-2024-088": (
        "INVOICE — Cortex Supply Chain Ltda\n"
        "Date: 2024-06-01 | Total: BRL 52,000.00\n"
        "WARNING: Same supplier and value as INV-CRT-2024-055 (2024-05-15) — duplicate risk"
    ),
}


@mcp.resource("docs://documents", mime_type="application/json")
def list_documents() -> list[str]:
    """List all document IDs available for audit."""
    return list(_DOCUMENTS.keys())


@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def fetch_document(doc_id: str) -> str:
    """Fetch the content of a specific document by ID."""
    if doc_id not in _DOCUMENTS:
        raise ValueError(f"Document '{doc_id}' not found. Available: {list(_DOCUMENTS.keys())}")
    return _DOCUMENTS[doc_id]
