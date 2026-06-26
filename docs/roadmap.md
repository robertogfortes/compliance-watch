# Roadmap — Post-MVP

Features deliberately out of scope for the MVP, documented to avoid scope creep during development.

## NOT in MVP (see SPEC non-objectives)

| Item | Reason excluded |
|---|---|
| ERP integration (SAP, TOTVS, Oracle) | Requires customer-specific connectors; out of portfolio demo scope |
| Multi-user authentication | Would require a full auth layer (OAuth, RBAC); file storage acceptable for MVP |
| Relational database | SQLite or Postgres would add ops complexity without changing the AI logic |
| Fine-tuning / model training | The project uses the API exclusively via prompting, RAG, and tool use |
| Automatic payment blocking | Non-objective by design: all output is a human recommendation, never an automatic action |

## Future phases (post-MVP)

### Phase 9 — ERP connector
- Read-only adapter for invoice export APIs (SAP Business One, TOTVS Protheus)
- Incremental ingestion into the RAG history index
- Scheduler: nightly batch audit of new documents

### Phase 10 — Multi-user dashboard
- Auth: OAuth 2.0 (Google Workspace or Azure AD)
- Per-analyst case queue
- Audit trail stored in PostgreSQL

### Phase 11 — Fine-grained tool streaming
- Full implementation of `streaming_tools.js` tool-call visualization
- Show tool name and input in the UI while Claude is "thinking" mid-turn

### Phase 12 — Compliance policy management UI
- Allow compliance managers to edit POL-PROC-* policies without touching code
- Policies stored as structured JSON, injected into the system prompt dynamically
- Policy versioning with rollback

### Phase 13 — Multi-language support
- Document ingestion in English, Portuguese, Spanish
- Audit reports in the analyst's preferred language
