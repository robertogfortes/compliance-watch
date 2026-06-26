"""
Generate a synthetic labeled evaluation dataset.

Uses Haiku (cheap) to generate realistic synthetic invoices and contracts,
both with and without deliberate anomalies. All entities are fictional.

Run:
    python evaluation/generate_dataset.py
Output:
    evaluation/dataset.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.claude_client import add_assistant_message, add_user_message, chat
from config import HAIKU

_NORMAL_PROMPT = """Generate a realistic synthetic financial document for compliance testing.

Rules:
- All company names, people, and identifiers must be FICTIONAL (use names like "Zynthar Corp", "Fluxion Services Ltda", "Meridian Logistics")
- No real CNPJs, tax IDs, or identifiable information
- The document should be NORMAL — no compliance anomalies

Document type: {doc_type}

Return JSON with:
- "document_text": full synthetic document as plain text
- "document_type": one of "invoice", "contract", "addendum"
- "has_anomaly": false
- "anomaly_type": null
- "expected_flags": []
- "solution_criteria": "The audit should find NO anomalies and report the document as compliant"
"""

_ANOMALY_PROMPT = """Generate a realistic synthetic financial document for compliance testing.

Rules:
- All company names, people, and identifiers must be FICTIONAL
- The document must contain EXACTLY ONE deliberate anomaly of the type specified

Document type: {doc_type}
Anomaly type: {anomaly_type}

Anomaly descriptions:
- "blocked_supplier": Supplier name matches one on the internal blocked list
- "duplicate_payment": Same supplier + same value as a previously submitted document
- "price_outlier": Value is more than 2x the historical average for the service category
- "missing_second_quote": Contract over BRL 50,000 with no mention of a second quotation
- "expired_contract": Addendum references a contract that has already expired

Return JSON with:
- "document_text": full synthetic document as plain text
- "document_type": one of "invoice", "contract", "addendum"
- "has_anomaly": true
- "anomaly_type": the anomaly type string
- "expected_flags": array of strings describing what should be flagged
- "solution_criteria": description of what a correct audit response must include
"""

_DOC_TYPES = ["invoice", "contract", "addendum"]
_ANOMALY_TYPES = [
    "blocked_supplier",
    "duplicate_payment",
    "price_outlier",
    "missing_second_quote",
    "expired_contract",
]


def _generate_case(prompt: str) -> dict:
    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```json")
    response = chat(messages, model=HAIKU, temperature=0.7, stop_sequences=["```"])
    raw = response.content[0].text if hasattr(response.content[0], "text") else ""
    return json.loads(raw.strip())


def generate_dataset(
    n_normal: int = 15,
    n_anomaly: int = 15,
    output_path: str = "evaluation/dataset.json",
) -> list[dict]:
    dataset = []

    print(f"Generating {n_normal} normal cases...")
    for i in range(n_normal):
        doc_type = _DOC_TYPES[i % len(_DOC_TYPES)]
        try:
            case = _generate_case(_NORMAL_PROMPT.format(doc_type=doc_type))
            case["id"] = f"normal_{i+1:03d}"
            dataset.append(case)
            print(f"  [{i+1}/{n_normal}] normal case generated")
        except Exception as e:
            print(f"  [{i+1}/{n_normal}] FAILED: {e}")

    print(f"Generating {n_anomaly} anomaly cases...")
    for i in range(n_anomaly):
        doc_type = _DOC_TYPES[i % len(_DOC_TYPES)]
        anomaly_type = _ANOMALY_TYPES[i % len(_ANOMALY_TYPES)]
        try:
            case = _generate_case(
                _ANOMALY_PROMPT.format(doc_type=doc_type, anomaly_type=anomaly_type)
            )
            case["id"] = f"anomaly_{i+1:03d}"
            dataset.append(case)
            print(f"  [{i+1}/{n_anomaly}] anomaly case ({anomaly_type}) generated")
        except Exception as e:
            print(f"  [{i+1}/{n_anomaly}] FAILED: {e}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"\nDataset saved: {output_path} ({len(dataset)} cases)")
    return dataset


if __name__ == "__main__":
    generate_dataset()
