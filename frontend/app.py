"""
ComplianceWatch web frontend — streaming audit reports with clickable citations.

Stack: Python (http.server) + Server-Sent Events for streaming + vanilla JS.
No framework dependencies — keeps the demo portable and simple.

Run:
    python frontend/app.py
Then open: http://localhost:8080
"""
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.claude_client import add_user_message, chat, with_cache, tools_with_cache
from prompts.system_auditor import SYSTEM_AUDITOR
from tools.schemas import ALL_TOOL_SCHEMAS
from config import DEFAULT_MODEL, MAX_ANALYSIS_TEMPERATURE

PORT = 8080
_STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


class ComplianceHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # suppress default access log noise

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path in ("/", "/index.html"):
            self._serve_file("index.html", "text/html")
        elif parsed.path == "/streaming_tools.js":
            self._serve_file("streaming_tools.js", "application/javascript")
        elif parsed.path == "/style.css":
            self._serve_file("style.css", "text/css")
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/audit":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body) if body else {}
            document_text = data.get("document", "").strip()

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            self._stream_audit(document_text)
        elif parsed.path == "/audit-sse":
            # GET-based SSE endpoint (query param: ?doc=...)
            params = parse_qs(parsed.query)
            document_text = params.get("doc", [""])[0]

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            self._stream_audit(document_text)
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _serve_file(self, filename: str, content_type: str):
        path = os.path.join(_STATIC_DIR, filename)
        if not os.path.exists(path):
            self.send_response(404)
            self.end_headers()
            return
        with open(path, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _sse(self, event: str, data: str):
        try:
            payload = f"event: {event}\ndata: {json.dumps(data)}\n\n"
            self.wfile.write(payload.encode("utf-8"))
            self.wfile.flush()
        except BrokenPipeError:
            pass

    def _stream_audit(self, document_text: str):
        if not document_text:
            self._sse("error", "No document provided.")
            self._sse("done", "")
            return

        try:
            messages = []
            add_user_message(
                messages,
                f"Audit the following document:\n\n<documento>\n{document_text}\n</documento>\n\n"
                "Use the compliance tools as needed. Cite every finding.",
            )

            self._sse("status", "Connecting to Claude…")

            # Stream the response token by token
            full_text = []
            for chunk in chat(
                messages,
                system=with_cache(SYSTEM_AUDITOR),
                model=DEFAULT_MODEL,
                temperature=MAX_ANALYSIS_TEMPERATURE,
                stream=True,
            ):
                full_text.append(chunk)
                self._sse("token", chunk)

            self._sse("done", "".join(full_text))

        except Exception as exc:
            self._sse("error", str(exc))
            self._sse("done", "")


def run():
    server = HTTPServer(("", PORT), ComplianceHandler)
    print(f"ComplianceWatch frontend: http://localhost:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run()
