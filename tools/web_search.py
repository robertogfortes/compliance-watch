"""
Web search tool — restricted to public price reference domains.

Never used to search for specific companies or individuals.
"""
import anthropic

from config import ANTHROPIC_API_KEY

_ALLOWED_DOMAINS: list[str] = [
    "economia.gov.br",
    "ibge.gov.br",
    "ipea.gov.br",
    "fgv.br",
    "portaltransparencia.gov.br",
]

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def web_search(query: str) -> dict:
    """
    Search public reference price index domains only.

    Raises ValueError for empty queries.
    Returns results list or error message if search fails.
    """
    if not query or not query.strip():
        raise ValueError("query cannot be empty")

    response = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "allowed_domains": _ALLOWED_DOMAINS,
        }],
        messages=[{"role": "user", "content": query.strip()}],
    )

    results = []
    for block in response.content:
        if block.type == "text":
            results.append({"type": "text", "content": block.text})
        elif hasattr(block, "type") and block.type == "tool_result":
            results.append({"type": "search_result", "content": str(block)})

    return {
        "query": query,
        "allowed_domains": _ALLOWED_DOMAINS,
        "results": results,
    }
