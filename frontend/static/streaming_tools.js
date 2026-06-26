/**
 * streaming_tools.js — streaming audit UI with clickable citations.
 *
 * Responsibilities:
 * - Open an SSE connection to /audit-sse
 * - Render tokens as they arrive (word-by-word streaming)
 * - Parse citation patterns in the completed text and make them clickable
 * - Display source citations in the side panel
 */

let _es = null;
let _buffer = "";
let _citationCount = 0;

// ─── Citation parsing ────────────────────────────────────────────────────────

// Matches patterns like:
//   citation: "some excerpt"
//   Citation: 'some text', line 5
//   cited_text: "value: BRL 17,300.00"
const CITATION_RE = /(?:citation|cited_text|source_excerpt)\s*:\s*["']([^"']{5,200})["']/gi;

function parseCitations(text) {
  const citations = [];
  let match;
  const re = new RegExp(CITATION_RE.source, "gi");
  while ((match = re.exec(text)) !== null) {
    citations.push({ id: `cite-${citations.length + 1}`, text: match[1] });
  }
  return citations;
}

function renderCitations(citations) {
  const panel = document.getElementById("citations-panel");
  const list = document.getElementById("citations-list");
  list.innerHTML = "";

  if (citations.length === 0) {
    panel.classList.add("hidden");
    return;
  }

  citations.forEach((c) => {
    const item = document.createElement("div");
    item.className = "citation-item";
    item.id = `panel-${c.id}`;
    item.innerHTML = `
      <div class="cite-source">Source excerpt</div>
      <div class="cite-text">"${escapeHtml(c.text)}"</div>
    `;
    list.appendChild(item);
  });

  panel.classList.remove("hidden");
}

// ─── Text rendering with inline citation markers ─────────────────────────────

function highlightCitationsInText(rawText, citations) {
  let html = escapeHtml(rawText);

  citations.forEach((c, i) => {
    const escaped = escapeHtml(c.text);
    const marker = `<span class="cited-text" onclick="scrollToPanel('panel-${c.id}')" title="Click to see citation">${escaped}</span>`;
    html = html.replace(escaped, marker);
  });

  // Wrap remaining citation: '...' patterns with a badge
  html = html.replace(
    /(?:citation|cited_text|source_excerpt)\s*:\s*(?:&quot;|&#39;)([^&]{5,200})(?:&quot;|&#39;)/gi,
    (match, excerpt) => {
      _citationCount++;
      return `<span class="citation-marker" title="${escapeHtml(excerpt)}">[cite ${_citationCount}]</span>`;
    }
  );

  return html;
}

function scrollToPanel(id) {
  const el = document.getElementById(id);
  if (el) {
    el.scrollIntoView({ behavior: "smooth", block: "center" });
    el.style.background = "#dbeafe";
    setTimeout(() => (el.style.background = ""), 1200);
  }
}

// ─── SSE streaming ────────────────────────────────────────────────────────────

function startAudit() {
  const doc = document.getElementById("document-input").value.trim();
  if (!doc) {
    showStatus("Please paste a document first.");
    return;
  }

  _buffer = "";
  _citationCount = 0;

  const btn = document.getElementById("audit-btn");
  btn.disabled = true;

  const reportSection = document.getElementById("report-section");
  const reportContent = document.getElementById("report-content");
  const indicator = document.getElementById("streaming-indicator");
  const citationsPanel = document.getElementById("citations-panel");

  reportSection.classList.remove("hidden");
  reportContent.textContent = "";
  citationsPanel.classList.add("hidden");
  indicator.classList.remove("done");

  showStatus("Sending document to Claude…");

  if (_es) _es.close();

  const encoded = encodeURIComponent(doc);
  _es = new EventSource(`/audit-sse?doc=${encoded}`);

  _es.addEventListener("status", (e) => {
    showStatus(JSON.parse(e.data));
  });

  _es.addEventListener("token", (e) => {
    _buffer += JSON.parse(e.data);
    reportContent.textContent = _buffer;
    reportContent.scrollTop = reportContent.scrollHeight;
  });

  _es.addEventListener("done", (e) => {
    _es.close();
    _es = null;
    btn.disabled = false;
    indicator.classList.add("done");
    hideStatus();

    const citations = parseCitations(_buffer);
    renderCitations(citations);
    reportContent.innerHTML = highlightCitationsInText(_buffer, citations);
  });

  _es.addEventListener("error", (e) => {
    const msg = e.data ? JSON.parse(e.data) : "Connection error";
    showStatus("Error: " + msg);
    btn.disabled = false;
    indicator.classList.add("done");
    if (_es) { _es.close(); _es = null; }
  });

  _es.onerror = () => {
    if (_es && _es.readyState === EventSource.CLOSED) {
      btn.disabled = false;
      indicator.classList.add("done");
    }
  };
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function showStatus(msg) {
  const bar = document.getElementById("status-bar");
  bar.textContent = msg;
  bar.classList.remove("hidden");
}

function hideStatus() {
  document.getElementById("status-bar").classList.add("hidden");
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
