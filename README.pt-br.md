# ComplianceWatch

> Sistema de auditoria de contratos e faturas com a API Claude.

ComplianceWatch sinaliza anomalias em documentos financeiros internos (faturas, contratos, aditivos) para revisão humana de conformidade. Cada constatação é rastreável a um trecho exato do documento com nível de confiança explícito — nunca uma acusação automática opaca.

**Todos os dados deste projeto são 100% sintéticos.** Nenhuma empresa real, pessoa física ou entidade pública é referenciada em qualquer lugar — código, conjuntos de dados, exemplos ou documentação. Veja [`docs/data-disclaimer.md`](docs/data-disclaimer.md).

---

[🇧🇷 Português](README.pt-br.md) · [🇺🇸 English](README.md)

---

## Screenshots

| Fatura duplicada — ALTO RISCO | Fornecedor bloqueado — ALTO RISCO |
|---|---|
| ![Auditoria fatura duplicada](docs/screenshots/02-duplicate-invoice-high-risk.png) | ![Auditoria fornecedor bloqueado](docs/screenshots/03-blocked-supplier-high-risk.png) |

| Valor atípico — ALTO RISCO | Contrato limpo — BAIXO RISCO |
|---|---|
| ![Auditoria valor atípico](docs/screenshots/04-price-outlier-high-risk.png) | ![Auditoria contrato limpo](docs/screenshots/05-clean-contract-low-risk.png) |

> **Experimente sem chave de API:** abra `frontend/demo.html` diretamente no navegador — sem servidor.
>
> **Modo real (Claude de verdade):** adicione `ANTHROPIC_API_KEY` ao `.env`, execute `python frontend/app.py` e abra `http://localhost:8080`. Veja [`docs/dev-setup.md`](docs/dev-setup.md) para o guia completo de migração de demo para produção.

## Arquitetura

```
Documento chega (fatura / contrato / aditivo)
  → [roteamento: classificar tipo do documento]   Haiku — barato, rápido
  → [extração de entidades]                       prefill + stop sequence → JSON limpo
  → [paralelização: verificações de conformidade] asyncio.gather → fornecedor bloqueado / valor atípico / duplicata
  → [recuperação: cruzamento com histórico]       BM25 + vetor cosseno → Reciprocal Rank Fusion
  → [encadeamento: rascunho → revisão de citações] duas chamadas; segunda passagem em temperature=0
  → relatório auditável final                     toda constatação tem uma citação
```

O **agente** de investigação profunda (`agent/investigacao_profunda.py`) é o único componente agêntico — acionado manualmente por um analista de conformidade em casos já sinalizados. Veja [`docs/architecture-decision.md`](docs/architecture-decision.md).

## Métricas de avaliação

> Execute `python evaluation/run_eval.py` após configurar seu `.env` para popular esta seção.

| Versão do prompt | Pontuação média (avaliador de modelo) | Taxa de aprovação de citações | Gate DoD |
|---|---|---|---|
| Baseline (stub) | — | — | Execute a avaliação para popular |

## Stack tecnológica

- **API Claude** — Haiku (roteamento/geração), Sonnet (análise), Opus (turnos do agente de alto risco)
- **VoyageAI** — embeddings `voyage-3-large` para busca semântica
- **BM25** + busca vetorial cosseno → recuperador híbrido com Reciprocal Rank Fusion
- **Servidor MCP** (`fastmcp`) — 3 ferramentas de conformidade + recursos + prompt
- **Suporte nativo a PDF + citações** — todo bloco de documento tem `citations.enabled=True`
- **Files API + execução de código** — detecção estatística de valores atípicos
- **Pensamento estendido** — ativado condicionalmente no agente de investigação

## Técnicas cobertas

Cada componente mapeia uma capacidade específica da API Claude:

| Técnica | Componente |
|---|---|
| Conversas multi-turno | `core/claude_client.py` — histórico de mensagens |
| Prompts de sistema | `prompts/system_auditor.py` — papel + políticas |
| Controle de temperatura | `MAX_ANALYSIS_TEMPERATURE = 0.2` em todas as chamadas de análise |
| Streaming | `frontend/app.py` + `streaming_tools.js` — UI token a token |
| Dados estruturados (prefill + stop) | `extraction/entities.py` — extração de JSON limpo |
| Uso de ferramentas | `tools/` + `core/run_conversation.py` — 4 ferramentas de conformidade |
| Schemas de ferramentas | `tools/schemas.py` — padrão `ToolParam` |
| RAG (chunking + embeddings) | `rag/` — VoyageAI + índice cosseno |
| Busca léxica BM25 | `rag/bm25_index.py` — busca exata por número de contrato |
| Recuperação híbrida (RRF) | `rag/retriever.py` — fusão semântica + léxica |
| Pensamento estendido | `agent/investigacao_profunda.py` — condicional, apenas em baixa confiança |
| Suporte a PDF | `extraction/pdf_reader.py` — blocos de documento |
| Citações | Obrigatório em toda chamada de análise de documento |
| Cache de prompts | `with_cache()` no prompt de sistema + `tools_with_cache()` |
| Files API + execução de código | `analysis/preco_stats.py` — estatísticas de valores atípicos |
| Servidor MCP | `mcp_server/` — ferramentas, recursos, prompts |
| Cliente MCP | `mcp_client.py` — gerenciador de contexto assíncrono |
| Workflow de roteamento | `pipeline.rotear_tipo_documento` |
| Workflow de paralelização | `pipeline.avaliar_politicas` — asyncio.gather |
| Workflow de encadeamento | `pipeline.gerar_e_revisar` — rascunho → revisão de citações |
| Agente | `agent/investigacao_profunda.py` — apenas quando flexibilidade é necessária |
| Pipeline de avaliação | `evaluation/` — gerar → avaliar → calcular média → gate DoD |
| Avaliador de modelo | `evaluation/graders/model_grader.py` — prefill impõe ordem de saída |
| Avaliador de código | `evaluation/graders/code_grader.py` — gate obrigatório de citações |
| Suporte a imagens | `extraction/scanned_pages.py` — análise de páginas digitalizadas |

## Configuração

```bash
git clone https://github.com/robertogfortes/compliance-watch.git
cd compliance-watch
cp .env.example .env
# preencha ANTHROPIC_API_KEY e VOYAGE_API_KEY
uv sync
python scripts/smoke_test.py   # verificar configuração
```

Veja [`docs/dev-setup.md`](docs/dev-setup.md) para instruções completas.

## Execução

```bash
# Interface web (streaming + citações clicáveis)
python frontend/app.py
# → http://localhost:8080

# Demo sem API (abre direto no navegador)
# Abra frontend/demo.html

# Pipeline via CLI
python -c "from pipeline import auditar_documento; print(auditar_documento(open('tests/fixtures/invoice_cortex_005.pdf', 'rb').read().decode('latin-1', errors='ignore'))['report'])"

# Agente de investigação profunda (manual, em casos sinalizados)
python agent/investigacao_profunda.py --case "Fatura duplicada suspeita" --document tests/fixtures/invoice_cortex_005.pdf

# Inspector MCP
mcp dev mcp_server/server.py

# Avaliação
python evaluation/generate_dataset.py
python evaluation/run_eval.py
```

## Inspiração

Este projeto foi desenvolvido como capstone aplicado durante o curso **[Building with the Claude API](https://verify.skilljar.com/c/bgpvpoxjuqsg)**. Cada componente do sistema mapeia diretamente um módulo coberto no curso — desde acesso básico à API e uso de ferramentas até RAG, pipelines de avaliação, servidores MCP e workflows agênticos multi-etapa.
