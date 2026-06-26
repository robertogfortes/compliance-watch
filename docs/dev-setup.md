# Development Setup

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (package manager)
- An Anthropic API key
- A VoyageAI API key (for Phase 3 embeddings)

## Installation

```bash
git clone https://github.com/robertofortes23/compliance-watch.git
cd compliance-watch

cp .env.example .env
# Edit .env and fill in ANTHROPIC_API_KEY and VOYAGE_API_KEY

uv sync
```

## Running the smoke test

```bash
python scripts/smoke_test.py
```

Expected output:
```
Running Phase 0 smoke tests...
[PASS] basic call: 'OK'
[PASS] multi-turn: '...42...'
[PASS] streaming: received N chunks
All tests passed.
```

## Generating synthetic fixtures

```bash
pip install reportlab  # one-time
python scripts/generate_fixtures.py
```

## Running the MCP server inspector

```bash
mcp dev mcp_server/server.py
```

Then open the MCP Inspector in your browser to test all 3 tools interactively.

## Registering the MCP server with Claude Code

```bash
claude mcp add compliance uv run mcp_server/server.py
```

## Generating the evaluation dataset

```bash
python evaluation/generate_dataset.py
# Output: evaluation/dataset.json (30 cases)
```

## Running the evaluation pipeline

```bash
python evaluation/run_eval.py --dataset evaluation/dataset.json --report evaluation/reports/baseline.json
```

## Running the web frontend

```bash
python frontend/app.py
# Open: http://localhost:8080
```

## Running the deep-investigation agent

```bash
python agent/investigacao_profunda.py --case "Suspicious invoice from Cortex Supply Chain" --document tests/fixtures/invoice_cortex_005.pdf
```

## Merge strategy

**All merges use the default merge commit** (not squash). This preserves per-phase commit history, which is part of the portfolio value. Set this once and never change:

```bash
git config merge.ff false
```

Do not use squash merge — the atomic commits within each phase are meaningful.

## Branch lifecycle

1. Branch from `main`: `git checkout -b phase-N-slug`
2. Implement atomically (one commit per component)
3. Push and open PR referencing the issue (`Closes #N`)
4. Merge → delete branch
5. Next phase begins only after the previous PR is merged
