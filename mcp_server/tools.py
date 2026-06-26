"""
MCP tool definitions — expose the three compliance lookup tools via @mcp.tool.

Registered on the shared `mcp` instance from server.py.
"""
from pydantic import Field

from mcp_server.server import mcp
from tools.fornecedor import consultar_fornecedor as _consultar_fornecedor
from tools.lista_bloqueio import consultar_lista_bloqueio as _consultar_lista_bloqueio
from tools.preco_medio import consultar_preco_medio as _consultar_preco_medio


@mcp.tool(
    name="consultar_fornecedor",
    description=(
        "Look up a supplier in the internal registry. Returns registration status, "
        "category, and compliance notes. Use to verify supplier is active and in good standing."
    ),
)
def consultar_fornecedor(
    supplier_id: str = Field(description="Supplier name or registry ID (e.g. 'SUP-001')"),
) -> dict:
    return _consultar_fornecedor(supplier_id)


@mcp.tool(
    name="consultar_lista_bloqueio",
    description=(
        "Check whether a supplier is on the blocked list. Returns blocked status and "
        "reason. Always check before approving a payment."
    ),
)
def consultar_lista_bloqueio(
    supplier_id: str = Field(description="Supplier name or registry ID to check"),
) -> dict:
    return _consultar_lista_bloqueio(supplier_id)


@mcp.tool(
    name="consultar_preco_medio",
    description=(
        "Return historical average price statistics for a service/product category. "
        "Use to detect outliers: flag values deviating more than 2 standard deviations."
    ),
)
def consultar_preco_medio(
    category: str = Field(description="Service or product category"),
    supplier_id: str | None = Field(default=None, description="Optional: filter to one supplier"),
) -> dict:
    return _consultar_preco_medio(category, supplier_id)
