"""
Statistical price outlier detection using the Files API and code execution.

Uploads the historical price CSV to the Claude Files API once, then asks Claude
to execute Python to compute mean/std_dev and flag outliers. This avoids sending
large datasets in every prompt.
"""
import anthropic

from config import ANTHROPIC_API_KEY, DEFAULT_MODEL, MAX_ANALYSIS_TEMPERATURE

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

_STATS_SYSTEM = (
    "You are a data analyst. You will receive a CSV file with historical invoice values "
    "for a specific service category. Use the code execution tool to compute descriptive "
    "statistics and determine if a given value is an outlier (> 2 standard deviations from mean). "
    "Return only valid JSON: {mean, std_dev, z_score, is_outlier: bool, verdict: string}."
)


def detect_price_outlier(category: str, value: float, history_csv: str) -> dict:
    """
    Upload history CSV via Files API and ask Claude to run Python statistics.

    history_csv: CSV string with columns 'date,value' for the given category.
    Returns: {mean, std_dev, z_score, is_outlier, verdict}
    """
    file_bytes = history_csv.encode("utf-8")
    uploaded = _client.beta.files.upload(
        file=("price_history.csv", file_bytes, "text/csv"),
    )

    try:
        response = _client.beta.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=1024,
            temperature=MAX_ANALYSIS_TEMPERATURE,
            system=_STATS_SYSTEM,
            tools=[{"type": "code_execution_20250522", "name": "code_execution"}],
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Category: {category}\n"
                            f"Value to check: BRL {value:,.2f}\n\n"
                            "The CSV file with historical prices is attached. "
                            "Compute mean and std_dev from the 'value' column. "
                            f"Then calculate z_score for {value} and determine if it's an outlier (|z| > 2). "
                            "Return JSON only."
                        ),
                    },
                    {
                        "type": "document",
                        "source": {"type": "file", "file_id": uploaded.id},
                    },
                ],
            }],
            betas=["files-api-2025-04-14", "code-execution-2025-05-22"],
        )

        import json
        for block in response.content:
            if hasattr(block, "text") and block.text:
                text = block.text.strip()
                if text.startswith("{"):
                    return json.loads(text)

        return {"error": "No JSON output from code execution", "is_outlier": False}

    finally:
        try:
            _client.beta.files.delete(uploaded.id)
        except Exception:
            pass
