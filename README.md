# linkedin-jobs-connector

This connector helps users connect their LinkedIn export data, pull the top 50-100 jobs from a provider, and surface recruiter or hiring-manager paths through 1st, 2nd, and 3rd degree connections.

## Overview

A portable Python project that can:

- ingest a user's LinkedIn connections export
- search the top 50-100 jobs from a provider
- surface recruiter and hiring-manager matches from 1st, 2nd, and 3rd degree connections
- expose the workflow through both HTTP and MCP-style stdio tools
- package itself as a zip bundle for upload into AI tooling

## What this project does

This project is designed to be reliable out of the box, even without external APIs:

- `demo` provider: works offline with bundled sample jobs
- `file` provider: reads jobs from a local JSON or CSV file
- connection matching: reads a LinkedIn connections CSV export and ranks likely recruiter or hiring-manager paths
- HTTP API: for local apps and scripts
- MCP server: for AI tools that support stdio tool servers

## Important constraint

LinkedIn does not provide a general public API for unrestricted job scraping and connection graph access. To keep this codebase portable and stable, the default implementation uses:

- a local CSV export for user connections
- a pluggable provider interface for job data

If you want live jobs, wire `JobProvider` to an approved provider or your internal data source.

## Project layout

```text
src/linkedin_connector/
  cache.py
  config.py
  http_api.py
  mcp_server.py
  models.py
  retry.py
  services.py
  providers/
  data/
examples/
tests/
scripts/
```

## Quick start

```bash
cd Linkedin_Connections
python3 -m unittest discover -s tests -p "test_*.py"
PYTHONPATH=src python3 -m linkedin_connector.http_api
```

Health check:

```bash
curl http://127.0.0.1:8765/health
```

Search demo jobs and enrich with connections:

```bash
curl -X POST http://127.0.0.1:8765/api/search-jobs \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "demo",
    "query": "software engineer",
    "location": "Chicago",
    "limit": 50,
    "connections_csv_path": "examples/connections.csv"
  }'
```

Use local file provider:

```bash
curl -X POST http://127.0.0.1:8765/api/search-jobs \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "file",
    "query": "product manager",
    "limit": 25,
    "jobs_file_path": "examples/jobs.json",
    "connections_csv_path": "examples/connections.csv"
  }'
```

## Connection CSV format

Expected headers:

```text
full_name,first_name,last_name,company,title,degree,profile_url,email,location
```

`degree` supports `1`, `2`, or `3`.

## MCP usage

Run the stdio MCP-compatible server:

```bash
PYTHONPATH=src python3 -m linkedin_connector.mcp_server
```

Supported tools:

- `health_check`
- `search_jobs`
- `match_connections`

## Package as zip

```bash
python3 scripts/package_zip.py
```

This creates:

```text
dist/linkedin_connector_bundle.zip
```

## Reliability measures

- thread-safe in-memory TTL cache
- bounded retries for provider calls
- structured JSON error responses
- non-fatal fallback behavior for missing optional fields
- standard-library runtime only

## Extension points

- add a new provider under `src/linkedin_connector/providers/`
- override host/port with environment variables
- swap the scoring heuristics in `services.py`
