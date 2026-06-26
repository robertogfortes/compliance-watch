"""
Tool schemas for all compliance lookup tools.

Convention: every schema variable is named <function_name>_schema and typed as ToolParam.
"""
from anthropic.types import ToolParam

consultar_fornecedor_schema = ToolParam({
    "name": "consultar_fornecedor",
    "description": (
        "Look up a supplier's registration details in the internal supplier registry. "
        "Returns name, CNPJ-equivalent synthetic ID, registration status, category, and "
        "any compliance notes. Use this when a document mentions a supplier and you need "
        "to verify whether they are active and in good standing."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "supplier_id": {
                "type": "string",
                "description": "Supplier name or synthetic registry ID (e.g. 'Synthex Supplies Ltda' or 'SUP-001').",
            }
        },
        "required": ["supplier_id"],
    },
})

consultar_lista_bloqueio_schema = ToolParam({
    "name": "consultar_lista_bloqueio",
    "description": (
        "Check whether a supplier appears on the internal blocked-supplier list. "
        "Returns blocked status (true/false), reason for blocking if applicable, and "
        "the date added to the list. Use this before approving any payment to verify "
        "the supplier has not been suspended or disqualified."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "supplier_id": {
                "type": "string",
                "description": "Supplier name or synthetic registry ID to check.",
            }
        },
        "required": ["supplier_id"],
    },
})

consultar_preco_medio_schema = ToolParam({
    "name": "consultar_preco_medio",
    "description": (
        "Retrieve the historical average price for a service or product category from "
        "the internal procurement history. Returns mean, standard deviation, min, max, "
        "and the number of historical transactions used. Use this to detect price "
        "outliers: flag if the document value deviates more than 2 standard deviations."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Service or product category (e.g. 'office equipment maintenance', 'consulting').",
            },
            "supplier_id": {
                "type": "string",
                "description": "Optional: narrow the history to a specific supplier.",
            },
        },
        "required": ["category"],
    },
})

web_search_schema = ToolParam({
    "name": "web_search",
    "description": (
        "Search public reference price indices for market price benchmarks. "
        "ONLY use allowed domains (public sector price indices, industry associations). "
        "Never search for specific companies or individuals — use internal tools for that."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query for public price reference data.",
            }
        },
        "required": ["query"],
    },
})

ALL_TOOL_SCHEMAS = [
    consultar_fornecedor_schema,
    consultar_lista_bloqueio_schema,
    consultar_preco_medio_schema,
]
