from __future__ import annotations

import json
import sys
import traceback
from typing import Any

from linkedin_connector.services import JobSearchService


SERVICE = JobSearchService()


TOOLS = [
    {
        "name": "health_check",
        "description": "Returns the health status of the connector.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "search_jobs",
        "description": "Search jobs and enrich them with recruiter and connection matches.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "provider": {"type": "string"},
                "query": {"type": "string"},
                "location": {"type": "string"},
                "limit": {"type": "integer"},
                "connections_csv_path": {"type": "string"},
                "jobs_file_path": {"type": "string"},
            },
        },
    },
    {
        "name": "match_connections",
        "description": "Match connections for a company, recruiter, and hiring manager.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "company": {"type": "string"},
                "recruiter_name": {"type": "string"},
                "hiring_manager_name": {"type": "string"},
                "connections_csv_path": {"type": "string"},
            },
            "required": ["company", "connections_csv_path"],
        },
    },
]


def write_message(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


def handle_call(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if tool_name == "health_check":
        return {"status": "ok", "service": "linkedin-jobs-connector"}

    if tool_name == "search_jobs":
        return SERVICE.search_jobs(
            provider_name=str(arguments.get("provider", "demo")),
            query=str(arguments.get("query", "")),
            location=str(arguments.get("location", "")),
            limit=int(arguments.get("limit", 50)),
            connections_csv_path=arguments.get("connections_csv_path"),
            jobs_file_path=arguments.get("jobs_file_path"),
        )

    if tool_name == "match_connections":
        return SERVICE.match_connections(
            company=str(arguments.get("company", "")),
            recruiter_name=str(arguments.get("recruiter_name", "")),
            hiring_manager_name=str(arguments.get("hiring_manager_name", "")),
            connections_csv_path=str(arguments.get("connections_csv_path", "")),
        )

    raise ValueError(f"unknown tool: {tool_name}")


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
            method = request.get("method")
            request_id = request.get("id")

            if method == "initialize":
                write_message(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "serverInfo": {"name": "linkedin-jobs-connector", "version": "0.1.0"},
                            "capabilities": {"tools": {}},
                        },
                    }
                )
                continue

            if method == "tools/list":
                write_message({"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOLS}})
                continue

            if method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                result = handle_call(str(tool_name), dict(arguments))
                write_message(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result),
                                }
                            ]
                        },
                    }
                )
                continue

            write_message(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"method not supported: {method}"},
                }
            )
        except Exception as exc:  # pragma: no cover - defensive path
            write_message(
                {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if "request" in locals() else None,
                    "error": {
                        "code": -32000,
                        "message": str(exc),
                        "data": traceback.format_exc(),
                    },
                }
            )


if __name__ == "__main__":
    main()
