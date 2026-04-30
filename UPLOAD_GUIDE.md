# Upload Guide

This project is packaged so users can either download the repository and use it directly, or upload the prepared zip bundle into compatible AI tools.

## One-click bundle download

The repository README includes a prominent `Download Connector Bundle` button.

It links directly to:

```text
https://github.com/ssudhendra/linkedin-jobs-connector/raw/main/dist/linkedin_connector_bundle.zip
```

## Fastest option

Download this file from the repository:

```text
dist/linkedin_connector_bundle.zip
```

Then upload that zip file into the AI tool if it supports:

- connector uploads
- plugin uploads
- project uploads
- knowledge bundle uploads
- MCP/local tool project imports

## GitHub download flow

1. Open the repository on GitHub.
2. Click `Code`.
3. Choose one of these:
   - `Download ZIP` to download the full repository
   - open `dist/linkedin_connector_bundle.zip` and download just the prepared bundle
4. If you downloaded the full repository zip, extract it and locate:

```text
dist/linkedin_connector_bundle.zip
```

## How to upload into AI tools

There are usually two supported patterns.

### 1. Direct zip upload

Use this file directly:

```text
dist/linkedin_connector_bundle.zip
```

This is the preferred path for tools that accept a single archive upload.

### 2. Folder import

If the AI tool expects an extracted folder instead of a zip:

1. Extract `dist/linkedin_connector_bundle.zip`
2. Upload the extracted folder
3. If the tool asks for a manifest or connector entry file, use:

```text
connector.manifest.json
```

## MCP-compatible AI tools

If the AI tool supports MCP stdio servers or local tool connectors, configure it with:

```text
Command: python3
Args: -m linkedin_connector.mcp_server
Env: PYTHONPATH=src
```

If the tool asks for the project root, point it to the extracted folder.

## HTTP-compatible AI tools

If the AI tool works with HTTP endpoints, start the API locally:

```bash
PYTHONPATH=src python3 -m linkedin_connector.http_api
```

Then use:

```text
Health URL: http://127.0.0.1:8765/health
API URL: http://127.0.0.1:8765/api/search-jobs
```

## Data to provide

For best results, provide:

- a LinkedIn connections CSV export
- optionally a jobs JSON or CSV file if using the `file` provider

Example files are included in:

```text
examples/connections.csv
examples/jobs.json
```

## Notes

- The bundled project works offline with the `demo` provider.
- The `file` provider is the simplest path for custom job datasets.
- Live LinkedIn scraping is not hardcoded in this project.
