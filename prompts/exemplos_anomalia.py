"""
Few-shot synthetic anomaly examples for the compliance auditor prompt.

All examples use fictional entities. These are injected into prompts as
<exemplos> XML blocks to demonstrate expected output format.
"""

EXEMPLOS_ANOMALIA = """<exemplos>

<exemplo id="1" tipo="blocked_supplier">
<documento>
INVOICE INV-ZYN-2024-033
Supplier: Zynthar Corp
Date: 2024-07-10
Total: BRL 18,500.00
Service: IT infrastructure consulting
</documento>
<analise_esperada>
Document summary: Invoice, Zynthar Corp, BRL 18,500.00, 2024-07-10, INV-ZYN-2024-033

POL-PROC-002 — Blocked supplier check:
  Finding: FLAG
  Confidence: 9/10
  Justification: "Zynthar Corp" appears on the blocked supplier list with reason \
"Regulatory non-compliance investigation initiated 2024-01-15." \
Citation: supplier name field, line 2.

Overall risk: HIGH
Recommended action: Suspend payment. Forward to legal and procurement for review.
</analise_esperada>
</exemplo>

<exemplo id="2" tipo="price_outlier">
<documento>
CONTRACT CTR-FLX-2024-009
Counterpart: Fluxion Services Ltda
Date: 2024-08-01
Service: Office cleaning — Building A and B
Monthly value: BRL 45,000.00
</documento>
<analise_esperada>
Document summary: Contract, Fluxion Services Ltda, BRL 45,000.00/month, 2024-08-01, CTR-FLX-2024-009

POL-PROC-003 — Price outlier check:
  Finding: FLAG
  Confidence: 8/10
  Justification: Historical average for facilities/cleaning is BRL 8,200 ± 400/month. \
BRL 45,000 is >90 standard deviations above the mean. \
Citation: "Monthly value: BRL 45,000.00", contract body.

Overall risk: HIGH
Recommended action: Escalate to procurement. Request independent market price benchmark.
</analise_esperada>
</exemplo>

<exemplo id="3" tipo="normal">
<documento>
INVOICE INV-MER-2024-017
Supplier: Meridian Logistics Group
Date: 2024-09-05
Total: BRL 15,200.00
Service: Express freight — quarterly batch
</documento>
<analise_esperada>
Document summary: Invoice, Meridian Logistics Group, BRL 15,200.00, 2024-09-05, INV-MER-2024-017

POL-PROC-001: N/A (invoice, not a contract)
POL-PROC-002: PASS — Meridian Logistics Group not on blocked list. Confidence: 10/10.
POL-PROC-003: PASS — BRL 15,200 within 1.2 std dev of logistics category average (BRL 15,500 ± 900). Confidence: 9/10.
POL-PROC-004: PASS — No duplicate found in 90-day window. Confidence: 10/10.

Overall risk: LOW
Recommended action: Approve for payment.
</analise_esperada>
</exemplo>

</exemplos>"""
