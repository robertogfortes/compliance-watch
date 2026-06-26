"""
Evaluation runner — grades every case in the dataset with both graders.

Usage:
    python evaluation/run_eval.py [--dataset evaluation/dataset.json] [--report evaluation/reports/baseline.json]

Definition of Done (DoD) gate:
    No prompt version enters production (demo) with average score < 7/10.
"""
import argparse
import json
import os
import sys
from datetime import datetime
from statistics import mean

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from evaluation.graders.code_grader import run_code_graders
from evaluation.graders.model_grader import grade_by_model


def run_eval(
    dataset: list[dict],
    run_prompt_fn,
    report_path: str | None = None,
) -> dict:
    """
    Run the evaluation pipeline over the dataset.

    run_prompt_fn(test_case) -> str  (the audit output to evaluate)
    Returns a results dict with per-case grades and averages.
    """
    results = []

    for i, test_case in enumerate(dataset):
        print(f"  [{i+1}/{len(dataset)}] Evaluating case {test_case.get('id', i)}...")
        try:
            output = run_prompt_fn(test_case)
            model_grade = grade_by_model(test_case, output)
            code_grade = run_code_graders(output)
            results.append({
                "id": test_case.get("id", str(i)),
                "has_anomaly": test_case.get("has_anomaly"),
                "anomaly_type": test_case.get("anomaly_type"),
                "output": output,
                "model_grade": model_grade,
                "code_grade": code_grade,
            })
        except Exception as exc:
            results.append({
                "id": test_case.get("id", str(i)),
                "error": str(exc),
                "model_grade": {"score": 0},
                "code_grade": {"citations_gate": 0, "overall_pass": False},
            })

    scores = [r["model_grade"]["score"] for r in results]
    avg_score = mean(scores) if scores else 0.0
    citations_pass_rate = mean(
        1 if r["code_grade"]["citations_gate"] == 10 else 0 for r in results
    )

    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_cases": len(results),
        "average_score": round(avg_score, 2),
        "citations_pass_rate": round(citations_pass_rate, 2),
        "dod_gate_passed": avg_score >= 7.0,
        "results": results,
    }

    print(f"\nAverage score: {avg_score:.2f}/10")
    print(f"Citations pass rate: {citations_pass_rate:.0%}")
    print(f"DoD gate (≥7.0): {'PASS' if summary['dod_gate_passed'] else 'FAIL'}")

    if report_path:
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"Report saved: {report_path}")

    return summary


def _stub_run_prompt(test_case: dict) -> str:
    """Placeholder prompt function — replace with real pipeline in Phase 5."""
    return (
        f"Audit of document type '{test_case.get('document_type', 'unknown')}': "
        "No anomalies detected. Confidence: 5/10. "
        "citation: 'Document reviewed end to end.'"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="evaluation/dataset.json")
    parser.add_argument("--report", default=f"evaluation/reports/eval_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json")
    args = parser.parse_args()

    if not os.path.exists(args.dataset):
        print(f"Dataset not found: {args.dataset}")
        print("Run: python evaluation/generate_dataset.py")
        sys.exit(1)

    with open(args.dataset, encoding="utf-8") as f:
        dataset = json.load(f)

    print(f"Running evaluation on {len(dataset)} cases...")
    run_eval(dataset, _stub_run_prompt, report_path=args.report)
