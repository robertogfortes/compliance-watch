"""Audit prompt template for contracts."""


def build_contract_prompt(document_text: str, supplier_history: str = "") -> str:
    history_block = (
        f"\n<historico_fornecedor>\n{supplier_history}\n</historico_fornecedor>"
        if supplier_history
        else ""
    )
    return f"""Audit the contract below against internal compliance policies.

<documento>
{document_text}
</documento>{history_block}

<politica_compliance>
Check ALL applicable policies:
- POL-PROC-001: Contract above BRL 50,000 must show evidence of at least 2 supplier quotations.
- POL-PROC-002: Supplier must not be on the blocked list.
- POL-PROC-003: Contract value must be within 2 std dev of category historical average.
- POL-PROC-005: If this is an addendum, parent contract must be active (not expired).
</politica_compliance>

Use the available tools to look up the supplier, check the blocked list, and retrieve pricing history.
Cite every claim with the exact document excerpt that supports it."""
