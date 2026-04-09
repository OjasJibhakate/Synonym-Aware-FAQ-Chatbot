from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

from chatbot_engine import FAQChatbot, FAQS


ROOT = Path(__file__).parent
STATIC_DIR = ROOT / "static"
CHATBOT = FAQChatbot(FAQS)


class FAQRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, file_path: Path, content_type: str) -> None:
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        route = urlparse(self.path).path

        if route == "/":
            self._send_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
            return

        if route == "/styles.css":
            self._send_file(STATIC_DIR / "styles.css", "text/css; charset=utf-8")
            return

        if route == "/script.js":
            self._send_file(
                STATIC_DIR / "script.js", "application/javascript; charset=utf-8"
            )
            return

        self.send_error(404, "Not Found")

    def do_POST(self) -> None:
        route = urlparse(self.path).path
        if route != "/api/chat":
            self.send_error(404, "Not Found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON payload"}, status=400)
            return

        message = str(payload.get("message", "")).strip()
        if not message:
            self._send_json({"error": "Message is required"}, status=400)
            return

        result = CHATBOT.answer_query(message)
        self._send_json(
            {
                "reply": result.answer,
                "intent": result.intent,
                "matched_question": result.matched_question,
                "similarity": round(result.similarity, 3),
                "processed_query": result.processed_query,
            }
        )


def run() -> None:
    server = HTTPServer(("127.0.0.1", 8000), FAQRequestHandler)
    print("FAQ chatbot running at http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    run()
