# ComplianceWatch

> Contract and invoice audit system using the Claude API.

ComplianceWatch flags anomalies in internal financial documents (invoices, contracts, addendums) for human compliance review. Every finding is traceable to an exact source excerpt with an explicit confidence level — never an opaque automatic accusation.

**All data used in this project is 100% synthetic.** No real company, person, or public entity is referenced anywhere — in code, datasets, examples, or documentation. See [`docs/data-disclaimer.md`](docs/data-disclaimer.md).

## Architecture

```
Document arrives (invoice / contract / addendum)
  → [entity extraction]                    (structured data + citations)
  → [routing: document type]               (routing workflow)
  → [parallelization: compliance policies] (parallel checks)
  → [retriever: cross-reference history]   (hybrid RAG)
  → [chaining: draft → cite review]        (chaining workflow)
  → final auditable report
```

The deep-investigation **agent** (`agent/investigacao_profunda.py`) is the only agentic component — triggered manually by a compliance analyst on an already-flagged case.

## Evaluation metrics

> Populated after the evaluation pipeline runs (Phase 4).

## Tech stack

- Claude API (Haiku · Sonnet · Opus) via `anthropic` SDK
- VoyageAI embeddings (`voyage-3-large`)
- BM25 lexical search + cosine vector search → Reciprocal Rank Fusion
- MCP server (`fastmcp`) for reusable tool exposure
- PDF native support + citations

## Setup

```bash
cp .env.example .env
# fill in ANTHROPIC_API_KEY and VOYAGE_API_KEY
uv sync
```

See [`docs/dev-setup.md`](docs/dev-setup.md) for full instructions.
