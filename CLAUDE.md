# ComplianceWatch — development context

## What this project is

ComplianceWatch is a compliance audit system for internal financial documents (invoices, contracts, addendums). It flags anomalies for human review. Every output is traceable to a source excerpt via the Claude citations API. Nothing is an automatic decision.

## Data policy (hard rule)

**All data must be 100% synthetic.** Zero real company names, supplier names, CNPJs, person names, or public entity names anywhere in code, datasets, prompts, or documentation. When generating synthetic data, use clearly fictional names like "Synthex Supplies Ltda" or "Contrato #SYN-2024-001".

## Architecture decisions

- **The pipeline is a Workflow, not an Agent** — routing → parallelization → chaining. Steps are known in advance.
- **The only Agent** lives in `agent/investigacao_profunda.py`, manually triggered by an analyst. It is not part of the automated pipeline.
- **citations.enabled=True** is mandatory in every document analysis call. The code grader enforces this as a hard gate, not a suggestion.
- **temperature ≤ 0.2** for all analysis calls. Haiku for cheap generation/triage; Sonnet for analysis; Opus only for high-risk review.

## Canonical patterns (do not deviate without explicit justification)

- Message helpers: `add_user_message` / `add_assistant_message` / `text_from_message` in `core/claude_client.py`
- Tool schemas: `function_name + "_schema"` as `ToolParam` in `tools/schemas.py`
- Tool loop: `run_tool` → `run_tools` → `run_conversation` (three separate functions, never inline)
- Prefill + stop: `add_assistant_message(messages, "```json")` then `chat(..., stop_sequences=["```"])`
- VectorIndex interface: must expose `add_vector`, `add_document`, `search` — compatible with `Retriever`
- Model grader output order: `strengths → weaknesses → reasoning → score` (prefill enforces this)
- MCP decorators: `@mcp.tool`, `@mcp.resource`, `@mcp.prompt` from `fastmcp`

## Git workflow

- No direct commits to `main`
- Branch per phase: `phase-N-short-slug`
- Commit types: `feat`, `fix`, `test`, `docs`, `refactor`, `eval`
- `eval(...)` prefix for commits that only touch `evaluation/reports/`
- PR closes the corresponding issue with `Closes #N`

## Commands

```bash
# Install dependencies
uv sync

# Run the MCP server inspector
mcp dev mcp_server/server.py

# Run evaluation
python evaluation/run_eval.py

# Smoke test (Phase 0)
python scripts/smoke_test.py
```
