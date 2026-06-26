/**
 * streaming_tools.js — streaming audit UI with clickable citations and demo mode.
 */

let _es = null;
let _buffer = "";
let _citationCount = 0;

// ─── Demo document presets ────────────────────────────────────────────────────

const DEMO_DOCS = {
  invoice_duplicate: `INVOICE
Document No: INV-CRT-2024-088
Supplier: Cortex Supply Chain Ltda
Issue Date: 2024-06-01
Service: Raw material batch #RM-2024-C88
Total: BRL 52,000.00

Note: Previous invoice INV-CRT-2024-055 submitted on 2024-05-15
for the same supplier and value (BRL 52,000.00).`,

  blocked_supplier: `INVOICE
Document No: INV-ORB-2024-014
Supplier: Orbita Services ME
Issue Date: 2024-07-08
Service: Janitorial and facilities management — Building B
Total: BRL 9,400.00`,

  price_outlier: `SERVICE CONTRACT
Contract No: CTR-FLX-2024-009
Counterpart: Fluxion Services Ltda
Effective Date: 2024-08-01
Expiry Date: 2025-07-31
Scope: Monthly office cleaning — Buildings A, B and C
Monthly Value: BRL 45,000.00
Annual Value: BRL 540,000.00

Second quotation: Not on file.`,

  contract_ok: `SERVICE CONTRACT
Contract No: CTR-VLT-2024-007
Counterpart: Veltron Technology Partners
Effective Date: 2024-01-10
Expiry Date: 2024-12-31
Scope: Annual software licensing and ERP support
Annual Value: BRL 96,000.00 (12 instalments of BRL 8,000.00)

Second quotation obtained: YES
  Ref: QUOT-VLT-2023-19 — BRL 98,400.00
  Ref: QUOT-AUR-2023-22 — BRL 101,000.00`,
};

// ─── Mock audit responses ─────────────────────────────────────────────────────

const MOCK_RESPONSES = {
  invoice_duplicate: {
    risk: "HIGH",
    report: `COMPLIANCE AUDIT REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Document Summary
  Type:            Invoice
  Document No:     INV-CRT-2024-088
  Supplier:        Cortex Supply Chain Ltda
  Value:           BRL 52,000.00
  Date:            2024-06-01

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Compliance Check Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POL-PROC-001 (Second quotation)
  Finding:    N/A — policy applies to contracts, not invoices.

POL-PROC-002 (Blocked supplier)
  Finding:    FLAG ⚠
  Confidence: 9/10
  Justification: Cortex Supply Chain Ltda (registry ID SUP-005) has status
  "suspended" in the internal supplier registry. Suspension reason: "duplicate
  billing investigation ongoing since 2024-02-28."
  citation: "Supplier: Cortex Supply Chain Ltda" — document header, line 3.

POL-PROC-003 (Price outlier)
  Finding:    PASS
  Confidence: 7/10
  Justification: BRL 52,000 is within 1.8 std dev of the raw materials
  category historical average (mean: BRL 50,000, σ: BRL 2,000).
  citation: "Total: BRL 52,000.00" — document footer.

POL-PROC-004 (Duplicate payment)
  Finding:    FLAG ⚠
  Confidence: 10/10
  Justification: Invoice INV-CRT-2024-055 (2024-05-15) was submitted by the
  same supplier (Cortex Supply Chain Ltda) for the identical value of BRL 52,000.00 —
  within the 90-day duplicate detection window. This is a confirmed duplicate risk.
  citation: "Previous invoice INV-CRT-2024-055 submitted on 2024-05-15 for the
  same supplier and value (BRL 52,000.00)." — document body.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Risk Assessment: HIGH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Two independent flags were raised:
1. Supplier is suspended (ongoing billing investigation)
2. Duplicate payment risk confirmed (identical supplier + value within 90 days)

Recommended Action for Analyst:
  SUSPEND payment immediately. Forward to legal and procurement teams.
  Cross-reference with INV-CRT-2024-055 to determine if both were processed.
  This finding requires human review before any payment is authorised.`,
    citations: [
      { label: "Supplier name — header", text: "Supplier: Cortex Supply Chain Ltda" },
      { label: "Invoice value — footer", text: "Total: BRL 52,000.00" },
      { label: "Duplicate note — document body", text: "Previous invoice INV-CRT-2024-055 submitted on 2024-05-15 for the same supplier and value (BRL 52,000.00)." },
    ],
    policies: [
      { tag: "N/A",  label: "POL-PROC-001", desc: "Second quotation — not applicable to invoices.", confidence: null },
      { tag: "FLAG", label: "POL-PROC-002", desc: "Supplier suspended (duplicate billing investigation since 2024-02-28).", confidence: "9/10" },
      { tag: "PASS", label: "POL-PROC-003", desc: "Value within 1.8 std dev of raw materials category average.", confidence: "7/10" },
      { tag: "FLAG", label: "POL-PROC-004", desc: "Duplicate confirmed: INV-CRT-2024-055 same supplier + same value, 17 days apart.", confidence: "10/10" },
    ],
  },

  blocked_supplier: {
    risk: "HIGH",
    report: `COMPLIANCE AUDIT REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Document Summary
  Type:            Invoice
  Document No:     INV-ORB-2024-014
  Supplier:        Orbita Services ME
  Value:           BRL 9,400.00
  Date:            2024-07-08

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Compliance Check Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POL-PROC-001 (Second quotation)
  Finding:    N/A — policy applies to contracts, not invoices.

POL-PROC-002 (Blocked supplier)
  Finding:    FLAG ⚠
  Confidence: 10/10
  Justification: Orbita Services ME (registry ID SUP-007) is on the
  internal blocked-supplier list. Reason: "Contract signed without mandatory
  second quotation (policy violation ref. POL-PROC-003)" — added 2023-11-14
  by internal_audit.
  citation: "Supplier: Orbita Services ME" — document header, line 3.

POL-PROC-003 (Price outlier)
  Finding:    PASS
  Confidence: 8/10
  Justification: BRL 9,400 is within the expected range for facilities
  services (historical mean: BRL 8,300, σ: BRL 700).
  citation: "Total: BRL 9,400.00" — document footer.

POL-PROC-004 (Duplicate payment)
  Finding:    PASS
  Confidence: 9/10
  Justification: No previous invoice from Orbita Services ME found in
  the 90-day window.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Risk Assessment: HIGH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recommended Action for Analyst:
  SUSPEND payment. This supplier is on the blocked list following an internal
  audit finding. Reactivation requires a formal compliance review and approval
  from the procurement director. This finding requires human review.`,
    citations: [
      { label: "Supplier name — header", text: "Supplier: Orbita Services ME" },
      { label: "Invoice value — footer", text: "Total: BRL 9,400.00" },
    ],
    policies: [
      { tag: "N/A",  label: "POL-PROC-001", desc: "Not applicable to invoices.", confidence: null },
      { tag: "FLAG", label: "POL-PROC-002", desc: "Orbita Services ME is on the blocked list (policy violation, added 2023-11-14).", confidence: "10/10" },
      { tag: "PASS", label: "POL-PROC-003", desc: "BRL 9,400 within expected range for facilities (mean BRL 8,300, σ 700).", confidence: "8/10" },
      { tag: "PASS", label: "POL-PROC-004", desc: "No duplicate found in 90-day window.", confidence: "9/10" },
    ],
  },

  price_outlier: {
    risk: "HIGH",
    report: `COMPLIANCE AUDIT REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Document Summary
  Type:            Contract
  Document No:     CTR-FLX-2024-009
  Supplier:        Fluxion Services Ltda
  Value:           BRL 45,000.00 / month (BRL 540,000.00 annual)
  Effective Date:  2024-08-01

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Compliance Check Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POL-PROC-001 (Second quotation — contract > BRL 50,000)
  Finding:    FLAG ⚠
  Confidence: 10/10
  Justification: Annual contract value of BRL 540,000 exceeds the BRL 50,000
  threshold. The document contains no evidence of a second quotation on file.
  citation: "Second quotation: Not on file." — document body.

POL-PROC-002 (Blocked supplier)
  Finding:    PASS
  Confidence: 10/10
  Justification: Fluxion Services Ltda does not appear on the blocked-supplier list.

POL-PROC-003 (Price outlier)
  Finding:    FLAG ⚠
  Confidence: 9/10
  Justification: Historical average for facilities/cleaning is BRL 8,200 ± 600/month.
  The contract value of BRL 45,000/month is +61 standard deviations above the mean —
  far beyond the 2 std dev threshold. This is a significant price anomaly.
  citation: "Monthly Value: BRL 45,000.00" — contract body.

POL-PROC-004 (Duplicate payment)
  Finding:    N/A — applies to invoices, not contracts.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Risk Assessment: HIGH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recommended Action for Analyst:
  DO NOT APPROVE. Two critical flags identified:
  1. No second quotation documented for a contract >BRL 50,000.
  2. Monthly value is >5x the market average for similar scope services.
  Escalate to procurement director. Request independent market benchmark
  and at minimum one competing quote before any signature is authorised.`,
    citations: [
      { label: "Missing quotation — document body", text: "Second quotation: Not on file." },
      { label: "Monthly value — contract body", text: "Monthly Value: BRL 45,000.00" },
    ],
    policies: [
      { tag: "FLAG", label: "POL-PROC-001", desc: "Annual value BRL 540k exceeds threshold — no second quotation documented.", confidence: "10/10" },
      { tag: "PASS", label: "POL-PROC-002", desc: "Fluxion Services Ltda not on blocked list.", confidence: "10/10" },
      { tag: "FLAG", label: "POL-PROC-003", desc: "BRL 45,000/month is +61 std dev above facilities mean (BRL 8,200 ± 600).", confidence: "9/10" },
      { tag: "N/A",  label: "POL-PROC-004", desc: "Duplicate check not applicable to contracts.", confidence: null },
    ],
  },

  contract_ok: {
    risk: "LOW",
    report: `COMPLIANCE AUDIT REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Document Summary
  Type:            Contract
  Document No:     CTR-VLT-2024-007
  Supplier:        Veltron Technology Partners
  Value:           BRL 96,000.00 annual (BRL 8,000/month)
  Effective Date:  2024-01-10

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Compliance Check Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

POL-PROC-001 (Second quotation — contract > BRL 50,000)
  Finding:    PASS
  Confidence: 10/10
  Justification: Annual value of BRL 96,000 exceeds threshold. Two quotations
  are on file: QUOT-VLT-2023-19 (BRL 98,400) and QUOT-AUR-2023-22 (BRL 101,000).
  Veltron submitted the lowest bid.
  citation: "Second quotation obtained: YES / Ref: QUOT-VLT-2023-19 — BRL 98,400.00 / Ref: QUOT-AUR-2023-22 — BRL 101,000.00" — contract footer.

POL-PROC-002 (Blocked supplier)
  Finding:    PASS
  Confidence: 10/10
  Justification: Veltron Technology Partners (registry ID SUP-003) is active.
  Compliance note on file: "Annual renewal pending review" — minor, does not block.
  citation: "Counterpart: Veltron Technology Partners" — document header.

POL-PROC-003 (Price outlier)
  Finding:    PASS
  Confidence: 9/10
  Justification: BRL 96,000/year for software licensing is within 0.3 std dev of
  the category historical average (mean: BRL 94,333, σ: BRL 5,200).
  citation: "Annual Value: BRL 96,000.00" — contract body.

POL-PROC-004 (Duplicate payment)
  Finding:    N/A — applies to invoices, not contracts.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Risk Assessment: LOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recommended Action for Analyst:
  Document appears compliant. All checks passed. Minor note: verify the annual
  renewal status of Veltron Technology Partners before the contract expiry
  date of 2024-12-31. No anomalies flagged — cleared for approval.`,
    citations: [
      { label: "Second quotation evidence — footer", text: "Second quotation obtained: YES / Ref: QUOT-VLT-2023-19 — BRL 98,400.00 / Ref: QUOT-AUR-2023-22 — BRL 101,000.00" },
      { label: "Supplier name — header", text: "Counterpart: Veltron Technology Partners" },
      { label: "Contract value — body", text: "Annual Value: BRL 96,000.00" },
    ],
    policies: [
      { tag: "PASS", label: "POL-PROC-001", desc: "Two quotations on file (QUOT-VLT-2023-19 and QUOT-AUR-2023-22). Veltron is lowest bidder.", confidence: "10/10" },
      { tag: "PASS", label: "POL-PROC-002", desc: "Veltron Technology Partners active (SUP-003). Annual renewal note — not blocking.", confidence: "10/10" },
      { tag: "PASS", label: "POL-PROC-003", desc: "BRL 96,000/year within 0.3 std dev of software licensing average.", confidence: "9/10" },
      { tag: "N/A",  label: "POL-PROC-004", desc: "Duplicate check not applicable to contracts.", confidence: null },
    ],
  },
};

// ─── Demo controls ────────────────────────────────────────────────────────────

function loadDemo(key) {
  document.getElementById("document-input").value = DEMO_DOCS[key] || "";
}

function runMockAudit() {
  const docText = document.getElementById("document-input").value.trim();
  if (!docText) { showStatus("Load a demo document first."); return; }

  // Detect which mock to use
  let key = "invoice_duplicate";
  for (const [k, text] of Object.entries(DEMO_DOCS)) {
    if (docText.includes(text.slice(10, 60).trim())) { key = k; break; }
  }
  const mock = MOCK_RESPONSES[key] || MOCK_RESPONSES["invoice_duplicate"];

  resetUI();
  showStatus("Connecting to Claude…");

  const reportSection = document.getElementById("report-section");
  const reportContent = document.getElementById("report-content");
  const indicator    = document.getElementById("streaming-indicator");
  reportSection.classList.remove("hidden");
  reportContent.textContent = "";
  indicator.classList.remove("done");

  // Simulate streaming: type the report character by character
  let i = 0;
  const text = mock.report;
  const interval = setInterval(() => {
    const chunkSize = Math.floor(Math.random() * 8) + 4;
    reportContent.textContent += text.slice(i, i + chunkSize);
    i += chunkSize;
    if (i >= text.length) {
      clearInterval(interval);
      _finishMockRender(mock);
    }
  }, 18);

  setTimeout(() => hideStatus(), 600);
}

function _finishMockRender(mock) {
  const indicator  = document.getElementById("streaming-indicator");
  const badge      = document.getElementById("risk-badge");
  const reportContent = document.getElementById("report-content");

  indicator.classList.add("done");

  // Risk badge
  badge.textContent = mock.risk + " RISK";
  badge.className = "risk-badge risk-" + mock.risk.toLowerCase();
  badge.classList.remove("hidden");

  // Render citations panel
  _renderCitations(mock.citations);

  // Render policy panel
  _renderPolicies(mock.policies);

  // Highlight cited text in report
  reportContent.innerHTML = _highlightCitations(
    escapeHtml(reportContent.textContent),
    mock.citations
  );
}

function _renderCitations(citations) {
  const panel = document.getElementById("citations-panel");
  const list  = document.getElementById("citations-list");
  list.innerHTML = "";
  if (!citations || citations.length === 0) { panel.classList.add("hidden"); return; }

  citations.forEach((c, i) => {
    const item = document.createElement("div");
    item.className = "citation-item";
    item.id = `panel-cite-${i}`;
    item.innerHTML = `<div class="cite-label">${escapeHtml(c.label)}</div><div class="cite-text">"${escapeHtml(c.text)}"</div>`;
    item.onclick = () => { item.style.background = "#dbeafe"; setTimeout(() => item.style.background = "", 1000); };
    list.appendChild(item);
  });
  panel.classList.remove("hidden");
}

function _renderPolicies(policies) {
  const panel = document.getElementById("policy-panel");
  const list  = document.getElementById("policy-list");
  list.innerHTML = "";
  if (!policies || policies.length === 0) { panel.classList.add("hidden"); return; }

  policies.forEach(p => {
    const row = document.createElement("div");
    row.className = "policy-row";
    const tagClass = p.tag === "FLAG" ? "tag-flag" : p.tag === "PASS" ? "tag-pass" : "tag-na";
    row.innerHTML = `
      <span class="policy-tag ${tagClass}">${p.tag}</span>
      <span class="policy-desc"><strong>${escapeHtml(p.label)}</strong> — ${escapeHtml(p.desc)}</span>
      ${p.confidence ? `<span class="policy-confidence">conf. ${p.confidence}</span>` : ""}
    `;
    list.appendChild(row);
  });
  panel.classList.remove("hidden");
}

function _highlightCitations(html, citations) {
  (citations || []).forEach(c => {
    const escaped = escapeHtml(c.text).slice(0, 60);
    html = html.replace(escaped, `<span class="cited-text">${escaped}</span>`);
  });
  return html;
}

// ─── Real SSE streaming (live API) ───────────────────────────────────────────

function startAudit() {
  const doc = document.getElementById("document-input").value.trim();
  if (!doc) { showStatus("Please paste a document first."); return; }

  resetUI();
  const btn = document.getElementById("audit-btn");
  btn.disabled = true;

  const reportSection = document.getElementById("report-section");
  const reportContent = document.getElementById("report-content");
  const indicator    = document.getElementById("streaming-indicator");
  reportSection.classList.remove("hidden");
  indicator.classList.remove("done");

  showStatus("Sending document to Claude…");

  if (_es) _es.close();
  _buffer = "";

  const encoded = encodeURIComponent(doc);
  _es = new EventSource(`/audit-sse?doc=${encoded}`);

  _es.addEventListener("status", e => showStatus(JSON.parse(e.data)));
  _es.addEventListener("token",  e => {
    _buffer += JSON.parse(e.data);
    reportContent.textContent = _buffer;
  });
  _es.addEventListener("done", e => {
    _es.close(); _es = null;
    btn.disabled = false;
    indicator.classList.add("done");
    hideStatus();

    // Basic citation parsing for live responses
    const citations = _parseCitations(_buffer);
    _renderCitations(citations);
    reportContent.innerHTML = _highlightCitations(escapeHtml(_buffer), citations);
  });
  _es.addEventListener("error", e => {
    const msg = e.data ? JSON.parse(e.data) : "Connection error";
    showStatus("Error: " + msg);
    btn.disabled = false;
    indicator.classList.add("done");
    if (_es) { _es.close(); _es = null; }
  });
}

function _parseCitations(text) {
  const re = /(?:citation|cited_text|source_excerpt)\s*:\s*["']([^"']{5,200})["']/gi;
  const out = [];
  let m;
  while ((m = re.exec(text)) !== null) {
    out.push({ label: `Citation ${out.length + 1}`, text: m[1] });
  }
  return out;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function resetUI() {
  _buffer = "";
  document.getElementById("report-content").textContent = "";
  document.getElementById("citations-panel").classList.add("hidden");
  document.getElementById("policy-panel").classList.add("hidden");
  document.getElementById("risk-badge").classList.add("hidden");
  document.getElementById("citations-list").innerHTML = "";
  document.getElementById("policy-list").innerHTML = "";
}

function showStatus(msg) {
  const bar = document.getElementById("status-bar");
  bar.textContent = msg;
  bar.classList.remove("hidden");
}

function hideStatus() {
  document.getElementById("status-bar").classList.add("hidden");
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function scrollToPanel(id) {
  const el = document.getElementById(id);
  if (el) {
    el.scrollIntoView({ behavior: "smooth", block: "center" });
    el.style.background = "#dbeafe";
    setTimeout(() => el.style.background = "", 1200);
  }
}
