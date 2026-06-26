"""
Main compliance audit pipeline — Workflow (not Agent).

Architecture: routing → parallelization → chaining
- rotear_tipo_documento: classifies document type
- avaliar_politicas: runs compliance checks in parallel (asyncio)
- gerar_e_revisar: drafts the report, then reviews citations in a second call
- auditar_documento: orchestrates the full pipeline

The deep-investigation agent (agent/investigacao_profunda.py) is separate and
manually triggered — it is NOT called from here.
"""
import asyncio
import json

from core.claude_client import (
    add_assistant_message,
    add_user_message,
    chat,
    text_from_message,
    with_cache,
    tools_with_cache,
)
from core.run_conversation import run_conversation
from extraction.entities import extract_entities_from_text
from prompts.system_auditor import SYSTEM_AUDITOR
from prompts.exemplos_anomalia import EXEMPLOS_ANOMALIA
from prompts.templates.nota_fiscal import build_invoice_prompt
from prompts.templates.contrato import build_contract_prompt
from prompts.templates.aditivo import build_addendum_prompt
from tools.schemas import ALL_TOOL_SCHEMAS
from config import DEFAULT_MODEL, HAIKU, MAX_ANALYSIS_TEMPERATURE


# ---------------------------------------------------------------------------
# Step 1 — Routing: classify document type
# ---------------------------------------------------------------------------

def rotear_tipo_documento(document_text: str) -> str:
    """
    Classify a document as 'invoice', 'contract', or 'addendum'.

    Uses Haiku (cheap) since this is a lightweight classification step.
    """
    messages = []
    add_user_message(
        messages,
        f"Classify this document. Return exactly one word: invoice, contract, or addendum.\n\n"
        f"<documento>\n{document_text[:2000]}\n</documento>",
    )
    add_assistant_message(messages, "The document type is: ")
    response = chat(messages, model=HAIKU, temperature=0.0, stop_sequences=["\n", "."])
    raw = text_from_message(response).strip().lower()

    for doc_type in ("invoice", "contract", "addendum"):
        if doc_type in raw:
            return doc_type
    return "invoice"  # safe default


# ---------------------------------------------------------------------------
# Step 2 — Parallelization: run compliance checks concurrently
# ---------------------------------------------------------------------------

async def _check_blocked_supplier(document_text: str, entities: dict) -> dict:
    supplier = entities.get("supplier", "unknown")
    messages = []
    add_user_message(
        messages,
        f"Check compliance policy POL-PROC-002 for this document.\n\n"
        f"Supplier identified: {supplier}\n\n"
        f"<documento>\n{document_text}\n</documento>\n\n"
        "Use the consultar_lista_bloqueio tool to check the supplier. "
        "Return JSON: {criterio, anomalo: bool, confianca: 0-10, justificativa}",
    )
    add_assistant_message(messages, "```json")
    response = chat(
        messages,
        system=with_cache(SYSTEM_AUDITOR),
        tools=tools_with_cache(ALL_TOOL_SCHEMAS),
        model=DEFAULT_MODEL,
        temperature=MAX_ANALYSIS_TEMPERATURE,
        stop_sequences=["```"],
    )
    raw = response.content[0].text if hasattr(response.content[0], "text") else "{}"
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        return {"criterio": "POL-PROC-002", "anomalo": False, "confianca": 0, "justificativa": raw}


async def _check_price_outlier(document_text: str, entities: dict) -> dict:
    messages = []
    add_user_message(
        messages,
        f"Check compliance policy POL-PROC-003 for this document.\n\n"
        f"<documento>\n{document_text}\n</documento>\n\n"
        "Use the consultar_preco_medio tool to retrieve historical pricing for the service category. "
        "Flag if the value deviates more than 2 standard deviations. "
        "Return JSON: {criterio, anomalo: bool, confianca: 0-10, justificativa}",
    )
    add_assistant_message(messages, "```json")
    response = chat(
        messages,
        system=with_cache(SYSTEM_AUDITOR),
        tools=tools_with_cache(ALL_TOOL_SCHEMAS),
        model=DEFAULT_MODEL,
        temperature=MAX_ANALYSIS_TEMPERATURE,
        stop_sequences=["```"],
    )
    raw = response.content[0].text if hasattr(response.content[0], "text") else "{}"
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        return {"criterio": "POL-PROC-003", "anomalo": False, "confianca": 0, "justificativa": raw}


async def _check_duplicate(document_text: str, entities: dict) -> dict:
    supplier = entities.get("supplier", "unknown")
    value = entities.get("value")
    messages = []
    add_user_message(
        messages,
        f"Check compliance policy POL-PROC-004 (duplicate payment) for this document.\n\n"
        f"Supplier: {supplier} | Value: {value}\n\n"
        f"<documento>\n{document_text}\n</documento>\n\n"
        "Use the consultar_fornecedor tool to retrieve the supplier history and look for "
        "duplicate submissions (same supplier + same value within 90 days). "
        "Return JSON: {criterio, anomalo: bool, confianca: 0-10, justificativa}",
    )
    add_assistant_message(messages, "```json")
    response = chat(
        messages,
        system=with_cache(SYSTEM_AUDITOR),
        tools=tools_with_cache(ALL_TOOL_SCHEMAS),
        model=DEFAULT_MODEL,
        temperature=MAX_ANALYSIS_TEMPERATURE,
        stop_sequences=["```"],
    )
    raw = response.content[0].text if hasattr(response.content[0], "text") else "{}"
    try:
        return json.loads(raw.strip())
    except json.JSONDecodeError:
        return {"criterio": "POL-PROC-004", "anomalo": False, "confianca": 0, "justificativa": raw}


async def avaliar_politicas(document_text: str, entities: dict) -> list[dict]:
    """
    Run all compliance checks in parallel (asyncio.gather).

    Time budget: total ≤ slowest individual check + 20%.
    """
    results = await asyncio.gather(
        _check_blocked_supplier(document_text, entities),
        _check_price_outlier(document_text, entities),
        _check_duplicate(document_text, entities),
    )
    return list(results)


# ---------------------------------------------------------------------------
# Step 3 — Chaining: draft → cite review
# ---------------------------------------------------------------------------

def gerar_e_revisar(
    document_text: str,
    doc_type: str,
    entities: dict,
    policy_results: list[dict],
) -> str:
    """
    Chain: generate draft report → verify every claim has a citation.

    Two separate API calls: first generates, second verifies citations.
    """
    supplier_history = ""
    if doc_type == "invoice":
        prompt = build_invoice_prompt(document_text, supplier_history)
    elif doc_type == "contract":
        prompt = build_contract_prompt(document_text, supplier_history)
    else:
        prompt = build_addendum_prompt(document_text)

    policy_summary = json.dumps(policy_results, indent=2)
    full_prompt = (
        f"{prompt}\n\n"
        f"<pre_analysis>\nParallel policy check results:\n{policy_summary}\n</pre_analysis>\n\n"
        f"{EXEMPLOS_ANOMALIA}\n\n"
        "Using the above analysis and examples, produce the final audit report."
    )

    messages = []
    add_user_message(messages, full_prompt)
    run_conversation(
        messages,
        tools=tools_with_cache(ALL_TOOL_SCHEMAS),
        system=with_cache(SYSTEM_AUDITOR),
        model=DEFAULT_MODEL,
        temperature=MAX_ANALYSIS_TEMPERATURE,
    )
    last_msg = next(
        m for m in reversed(messages)
        if m["role"] == "assistant" and isinstance(m["content"], list)
    )
    draft = "\n".join(
        block.text for block in last_msg["content"]
        if hasattr(block, "type") and block.type == "text"
    )

    # Second call — citation review pass
    review_messages = []
    add_user_message(
        review_messages,
        f"Review the audit report below. Verify that every anomaly claim has a citation "
        f"pointing to the exact document excerpt that supports it. "
        f"If any claim lacks a citation, add it. Do not change any findings or scores.\n\n"
        f"<draft_report>\n{draft}\n</draft_report>",
    )
    review_response = chat(
        review_messages,
        system=with_cache(SYSTEM_AUDITOR),
        model=DEFAULT_MODEL,
        temperature=0.0,
    )
    return text_from_message(review_response)


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def auditar_documento(document_text: str) -> dict:
    """
    Full audit pipeline for a plain-text document.

    Returns:
        {doc_type, entities, policy_results, report}
    """
    # Routing
    doc_type = rotear_tipo_documento(document_text)

    # Entity extraction
    entities = extract_entities_from_text(document_text)

    # Parallel policy checks
    policy_results = asyncio.run(avaliar_politicas(document_text, entities))

    # Draft + citation review chain
    report = gerar_e_revisar(document_text, doc_type, entities, policy_results)

    return {
        "doc_type": doc_type,
        "entities": entities,
        "policy_results": policy_results,
        "report": report,
    }
