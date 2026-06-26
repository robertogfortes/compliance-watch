"""
Code-based (deterministic) graders for structural output validation.

The citations gate is a hard requirement: any anomaly claim without a citations
block scores 0 and must not proceed to production.
"""
import json
import re


def validate_json(text: str) -> int:
    """Return 10 if text is valid JSON, 0 otherwise."""
    try:
        json.loads(text.strip())
        return 10
    except json.JSONDecodeError:
        return 0


def validate_citations_present(output: str) -> int:
    """
    Return 10 if every anomaly claim in the output has an associated citation.

    Heuristic: look for 'anomaly' or 'flagged' or 'violation' mentions and
    check that a 'cited_text' or 'citation' key appears nearby (within 500 chars).
    Returns 0 if any anomaly claim lacks a citation — this is the hard gate.
    """
    anomaly_pattern = re.compile(
        r"(anomal|flagged|violation|suspicious|bloqueado|duplicat|outlier)",
        re.IGNORECASE,
    )
    citation_pattern = re.compile(
        r"(cited_text|citation|source_excerpt|document_title|cite)",
        re.IGNORECASE,
    )

    positions = [m.start() for m in anomaly_pattern.finditer(output)]
    if not positions:
        return 10  # No anomaly claims — no citations needed

    for pos in positions:
        window = output[max(0, pos - 200): pos + 500]
        if not citation_pattern.search(window):
            return 0  # Anomaly claim without nearby citation — hard fail

    return 10


def validate_confidence_level(output: str) -> int:
    """Return 10 if the output contains a numeric confidence level, 0 otherwise."""
    if re.search(r"\b(confidence|confianca|score)[:\s]+\d", output, re.IGNORECASE):
        return 10
    if re.search(r"\b\d+\s*/\s*10\b", output):
        return 10
    return 0


def run_code_graders(output: str) -> dict:
    """
    Run all deterministic checks and return a results dict.

    citations_gate=0 means the output MUST NOT proceed to production.
    """
    return {
        "citations_gate": validate_citations_present(output),
        "confidence_present": validate_confidence_level(output),
        "overall_pass": (
            validate_citations_present(output) == 10
            and validate_confidence_level(output) == 10
        ),
    }
