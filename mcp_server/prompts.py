"""
MCP prompt definitions — pre-tested prompt templates accessible via /auditar in the UI.
"""
from mcp.server.fastmcp.prompts import base
from pydantic import Field

from mcp_server.server import mcp


@mcp.prompt(
    name="auditar",
    description="Run a full compliance audit on a document. Provide the document ID.",
)
def auditar_documento(
    doc_id: str = Field(description="Document ID to audit (e.g. 'INV-SYN-2024-001')"),
) -> list[base.Message]:
    prompt = (
        f"Audit document {doc_id} using the compliance tools available.\n\n"
        "Follow these steps:\n"
        "1. Fetch the document content using the docs://documents resource.\n"
        "2. Check the supplier against the registry (consultar_fornecedor).\n"
        "3. Check the supplier against the blocked list (consultar_lista_bloqueio).\n"
        "4. Check the document value against historical prices (consultar_preco_medio).\n"
        "5. Report findings with confidence level (0–10) for each check.\n"
        "6. For any anomaly flagged, cite the exact document excerpt that triggered it.\n\n"
        "This is a compliance review for human analyst inspection — not an automatic decision."
    )
    return [base.UserMessage(prompt)]
