from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from linkedin_connector.config import SETTINGS
from linkedin_connector.services import JobSearchService


SERVICE = JobSearchService()


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, object]) -> None:
    encoded = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(encoded)))
    handler.end_headers()
    handler.wfile.write(encoded)


class RequestHandler(BaseHTTPRequestHandler):
    server_version = "LinkedInConnector/0.1"

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            json_response(self, HTTPStatus.OK, {"status": "ok", "service": "linkedin-jobs-connector"})
            return
        json_response(self, HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length) if content_length else b"{}"
            payload = json.loads(raw_body.decode("utf-8"))

            if self.path == "/api/search-jobs":
                result = SERVICE.search_jobs(
                    provider_name=str(payload.get("provider", "demo")),
                    query=str(payload.get("query", "")),
                    location=str(payload.get("location", "")),
                    limit=int(payload.get("limit", SETTINGS.default_limit)),
                    connections_csv_path=self._optional_str(payload, "connections_csv_path"),
                    jobs_file_path=self._optional_str(payload, "jobs_file_path"),
                )
                json_response(self, HTTPStatus.OK, result)
                return

            if self.path == "/api/match-connections":
                result = SERVICE.match_connections(
                    company=str(payload.get("company", "")),
                    recruiter_name=str(payload.get("recruiter_name", "")),
                    hiring_manager_name=str(payload.get("hiring_manager_name", "")),
                    connections_csv_path=str(payload.get("connections_csv_path", "")),
                )
                json_response(self, HTTPStatus.OK, result)
                return

            json_response(self, HTTPStatus.NOT_FOUND, {"error": "not_found"})
        except Exception as exc:
            json_response(
                self,
                HTTPStatus.BAD_REQUEST,
                {
                    "error": "request_failed",
                    "message": str(exc),
                },
            )

    def log_message(self, format: str, *args: object) -> None:
        return

    @staticmethod
    def _optional_str(payload: dict[str, object], key: str) -> str | None:
        value = payload.get(key)
        if value is None:
            return None
        text = str(value).strip()
        return text or None


def main() -> None:
    server = ThreadingHTTPServer((SETTINGS.host, SETTINGS.port), RequestHandler)
    print(f"HTTP API listening on http://{SETTINGS.host}:{SETTINGS.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
