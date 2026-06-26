# Testing Guide

## MCP Inspector — verifying the MCP server

```bash
mcp dev mcp_server/server.py
```

The inspector opens a browser UI. Verify:

| Tool | Test input | Expected result |
|---|---|---|
| `consultar_fornecedor` | `{"supplier_id": "SUP-001"}` | Returns Synthex Supplies Ltda, status: active |
| `consultar_lista_bloqueio` | `{"supplier_id": "SUP-005"}` | Returns blocked: true, reason: duplicate billing |
| `consultar_preco_medio` | `{"category": "consulting"}` | Returns mean ~28,500, std_dev ~2,300 |

Resources:
- `docs://documents` → list of 5 document IDs
- `docs://documents/INV-SYN-2024-001` → Synthex invoice content

Prompts:
- `/auditar INV-CRT-2024-088` → 5-step audit walkthrough for the duplicate-risk invoice

## Smoke test

```bash
python scripts/smoke_test.py
```

Three tests: basic single-turn call, multi-turn conversation, streaming.

## Pipeline manual test

```python
from pipeline import auditar_documento

result = auditar_documento("""
INVOICE INV-SYN-2024-001
Supplier: Synthex Supplies Ltda
Date: 2024-03-15
Total: BRL 17,300.00
Items: Office equipment maintenance + Network infrastructure upgrade
""")
print(result["report"])
```

## Evaluation run

```bash
python evaluation/generate_dataset.py     # generate 30 synthetic cases
python evaluation/run_eval.py             # grade them; prints average score and DoD gate
```

DoD gate: average score must be ≥ 7.0/10 before any prompt is considered production-ready.

## Frontend manual test

1. `python frontend/app.py`
2. Open `http://localhost:8080`
3. Paste the content of `tests/fixtures/invoice_cortex_005.pdf` (or any text)
4. Click "Run Audit"
5. Verify:
   - Tokens appear progressively (streaming)
   - Citations appear in the side panel
   - Clicking a citation scrolls to the source
