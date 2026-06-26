"""
Model-based grader for audit output quality.

Always requests reasoning BEFORE the score (prefill enforces key order).
Output order is fixed: strengths → weaknesses → reasoning → score.
Never change this order — the prefill contract depends on it.
"""
import json

from core.claude_client import add_assistant_message, add_user_message, chat
from config import HAIKU


def grade_by_model(test_case: dict, output: str) -> dict:
    """
    Grade an audit output against its test case.

    Returns dict with keys: strengths, weaknesses, reasoning, score (1–10).
    """
    eval_prompt = f"""You are an expert compliance audit reviewer. Evaluate the audit response below.

<task>{test_case.get("solution_criteria", "Produce a correct compliance audit report")}</task>

<expected_anomaly_present>{test_case.get("has_anomaly", False)}</expected_anomaly_present>
<expected_flags>{json.dumps(test_case.get("expected_flags", []))}</expected_flags>

<audit_response>{output}</audit_response>

Score the response on these criteria:
1. Correct anomaly detection (or correct clean bill if no anomaly)
2. Presence of citations linking claims to document text
3. Explicit confidence level for each finding
4. No fabricated findings unsupported by the document

Provide your evaluation as JSON with EXACTLY these keys in this order:
- "strengths": array of 1–3 specific positive aspects
- "weaknesses": array of 1–3 specific issues, or ["none"] if perfect
- "reasoning": concise explanation of the score
- "score": integer from 1 to 10
"""

    messages = []
    add_user_message(messages, eval_prompt)
    add_assistant_message(messages, "```json")
    response = chat(messages, model=HAIKU, temperature=0.0, stop_sequences=["```"])
    raw = response.content[0].text if hasattr(response.content[0], "text") else ""
    return json.loads(raw.strip())
