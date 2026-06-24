"""本機 HTTP：POST /api/v1/dispatch（與 CLI/TG 同一 dispatch）。"""

from __future__ import annotations

import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ai_company.adapters.deps import AppDeps
from ai_company.adapters.web.inbound import dispatch_json
from ai_company.config import AppSettings

logger = logging.getLogger(__name__)


def make_handler(settings: AppSettings, deps: AppDeps):
    class DispatchHandler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:  # noqa: A003
            logger.info("%s - %s", self.address_string(), format % args)

        def _check_auth(self) -> bool:
            key = settings.web_api_key.strip()
            if not key:
                return True
            auth = self.headers.get("Authorization", "")
            expected = f"Bearer {key}"
            return auth == expected

        def _send_json(self, status: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            if self.path.rstrip("/") == "/health":
                self._send_json(200, {"ok": True})
                return
            self._send_json(404, {"success": False, "error_code": "not_found"})

        def do_POST(self) -> None:  # noqa: N802
            if self.path.rstrip("/") != "/api/v1/dispatch":
                self._send_json(404, {"success": False, "error_code": "not_found"})
                return
            if not self._check_auth():
                self._send_json(401, {"success": False, "error_code": "unauthorized"})
                return
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                body = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError:
                self._send_json(400, {"success": False, "error_code": "invalid_json"})
                return
            if not isinstance(body, dict):
                self._send_json(400, {"success": False, "error_code": "invalid_body"})
                return
            result = dispatch_json(body, deps)
            status = 200 if result.get("success", True) else 400
            self._send_json(status, result)

    return DispatchHandler


def serve(settings: AppSettings, *, host: str, port: int) -> None:
    deps = AppDeps(settings=settings)
    handler = make_handler(settings, deps)
    server = ThreadingHTTPServer((host, port), handler)
    logger.info("Web adapter 監聽 http://%s:%s", host, port)
    server.serve_forever()
