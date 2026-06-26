"""Audit prompt template for contract addendums."""


def build_addendum_prompt(document_text: str, parent_contract_text: str = "") -> str:
    parent_block = (
        f"\n<contrato_original>\n{parent_contract_text}\n</contrato_original>"
        if parent_contract_text
        else ""
    )
    return f"""Audit the contract addendum below against internal compliance policies.

<documento>
{document_text}
</documento>{parent_block}

<politica_compliance>
Check:
- POL-PROC-002: Supplier must not be on the blocked list.
- POL-PROC-003: New value (original + adjustment) must be within acceptable range.
- POL-PROC-005: The referenced parent contract must be active and not expired.
  If parent contract text is not provided, use available tools to look it up.
</politica_compliance>

Use the available tools to verify supplier status and pricing history.
Cite every claim with the exact document excerpt that supports it."""
