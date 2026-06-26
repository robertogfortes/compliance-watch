# Data Disclaimer — Synthetic Data Declaration

## Declaration

**All data in this project is 100% synthetic.** No real company, supplier, person, public entity, tax registration number (CNPJ or equivalent), or government body is referenced anywhere in this repository — including code, datasets, test fixtures, prompts, examples, screenshots, or documentation.

Synthetic entity names used in this project:

- Synthex Supplies Ltda
- Nexoria Consulting S.A.
- Veltron Technology Partners
- Auramid Facilities Ltda
- Cortex Supply Chain Ltda
- Helix Logistics Group
- Orbita Services ME
- Zynthar Corp
- Fluxion Services Ltda
- Meridian Logistics Group

All contract numbers, invoice numbers, dates, values, and registry IDs are fictional.

## Pre-publication checklist

Run this checklist manually before every public release of the repository:

- [ ] No real company name appears in `evaluation/dataset.json`
- [ ] No real company name appears in `tests/fixtures/`
- [ ] No real CNPJ, tax ID, or registry number appears in any file
- [ ] No real person's name appears in any file
- [ ] No real government entity is cited as a reference in any prompt or example
- [ ] `evaluation/reports/*.json` files reviewed — no real entities leaked in model-generated content
- [ ] Screenshots in `docs/` (if any) do not show real entity names
- [ ] `git log --all --oneline` reviewed — no sensitive data in commit messages

## Why this matters

ComplianceWatch analyses financial documents for anomalies. Using real company names or real compliance incidents — even as examples — could constitute defamation, breach confidentiality obligations, or create legal liability. The synthetic-data policy eliminates this risk entirely.
