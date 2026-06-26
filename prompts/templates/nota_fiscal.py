"""Audit prompt template for invoices (nota fiscal)."""


def build_invoice_prompt(document_text: str, supplier_history: str = "") -> str:
    history_block = (
        f"\n<historico_fornecedor>\n{supplier_history}\n</historico_fornecedor>"
        if supplier_history
        else ""
    )
    return f"""Audit the invoice below against internal compliance policies.

<documento>
{document_text}
</documento>{history_block}

<politica_compliance>
Check: POL-PROC-002 (blocked supplier), POL-PROC-003 (price outlier), POL-PROC-004 (duplicate payment).
POL-PROC-001 does not apply to invoices.
</politica_compliance>

Use the available tools to look up the supplier, check the blocked list, and retrieve historical pricing.
Cite every claim with the exact document excerpt that supports it."""
