# Architecture Decision: Workflow vs. Agent

## Decision

The main compliance audit pipeline (`pipeline.py`) is a **Workflow**. The deep-investigation component (`agent/investigacao_profunda.py`) is the **only Agent**.

## Rationale

### Why the pipeline is a Workflow

The main pipeline steps are deterministic and known before execution:

```
document arrives
  → routing (classify type)
  → entity extraction (structured fields)
  → parallel policy checks (blocked supplier / price outlier / duplicate)
  → retriever (cross-reference history)
  → draft report
  → citation review
  → final report
```

Every step has a defined input and output. The number of API calls is bounded. There is no decision point where Claude needs to choose a different path based on unknown intermediate state. Workflows are preferred here because they are more predictable, testable, and auditable — which is especially important for a compliance system.

### Why the investigation agent is an Agent

The deep-investigation component (`agent/investigacao_profunda.py`) is the only case where an Agent is appropriate:

1. **Unknown number of tool calls**: A simple blocked-supplier case may need 2 tool calls. A suspected duplicate payment ring may need 10+. The agent decides.
2. **Analyst interaction**: The agent may pause and ask the analyst for additional context (e.g., "What was the original contract date?"). This is not a fixed step — it happens when the agent determines it lacks information.
3. **Extended thinking**: The agent activates extended thinking automatically when its confidence drops below a threshold. This is a meta-level decision that a fixed workflow cannot make.
4. **Manual trigger**: It is never called from `pipeline.py`. An analyst runs it deliberately on an already-flagged case.

### Entry points and auth

| Component | Trigger | Auth |
|---|---|---|
| `pipeline.py` | Automated / scheduled | API key (multi-user) |
| `agent/investigacao_profunda.py` | Manual, by analyst | Personal plan / OAuth |

The same `mcp_server/` serves both — only the MCP host differs.

## Reference

This decision directly follows the principle: *"prioritise workflows when possible; use agents only when flexibility is genuinely required."*
