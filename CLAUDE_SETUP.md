# Claude Setup

This guide explains how to use `linkedin-jobs-connector` with Claude Desktop on macOS through a local MCP server, including official LinkedIn OAuth sign-in.

## What this setup supports

This repository currently supports:

- Claude Desktop
- local MCP server setup
- official LinkedIn OAuth sign-in
- local files for LinkedIn connections and optional jobs datasets

This repository does not currently provide:

- a Claude `.dxt` extension package
- a hosted remote MCP deployment for `claude.ai`
- unrestricted LinkedIn jobs or 2nd/3rd degree connection APIs

## Prerequisites

Before configuring Claude, make sure you have:

- Claude Desktop installed
- Python 3.10 or later installed
- this repository downloaded or cloned locally

Check Python:

```bash
python3 --version
```

## Recommended local folder

Put the extracted project in a stable path, for example:

```text
/Users/sudhendrasoanpet/Downloads/linkedin-jobs-connector
```

If you cloned the repo directly, use that repo path instead.

## Step 1. Download the connector

Use the direct bundle link from the GitHub README button, or download the repo and extract it.

Direct bundle link:

```text
https://github.com/ssudhendra/linkedin-jobs-connector/raw/main/dist/linkedin_connector_bundle.zip
```

## Step 2. Extract the bundle

Example:

```bash
mkdir -p /Users/sudhendrasoanpet/Downloads/linkedin-jobs-connector
unzip linkedin_connector_bundle.zip -d /Users/sudhendrasoanpet/Downloads/linkedin-jobs-connector
```

If the files are extracted under an extra nested directory, use the final folder that contains:

```text
src/
examples/
README.md
connector.manifest.json
```

## Step 3. Verify the project works before Claude

Run:

```bash
cd /Users/sudhendrasoanpet/Downloads/linkedin-jobs-connector
python3 -m unittest discover -s tests -p "test_*.py"
```

Expected result:

```text
OK
```

You can also manually start the MCP server:

```bash
cd /Users/sudhendrasoanpet/Downloads/linkedin-jobs-connector
PYTHONPATH=src python3 -m linkedin_connector.mcp_server
```

If it starts without errors and waits for input, that is expected.

## Step 4. Open Claude Desktop config

Claude Desktop uses a local config file named:

```text
claude_desktop_config.json
```

On macOS, open Claude Desktop and use its MCP/local server settings flow to edit the config file.

If you already have a config file, do not remove your existing servers. Just add the new server entry shown below.

## Step 5. Add this exact MCP server block

If the config file is empty, use this:

```json
{
  "mcpServers": {
    "linkedin-jobs-connector": {
      "command": "/bin/zsh",
      "args": [
        "-lc",
        "cd '/Users/sudhendrasoanpet/Downloads/linkedin-jobs-connector' && PYTHONPATH=src python3 -m linkedin_connector.mcp_server"
      ],
      "env": {
        "LINKEDIN_CLIENT_ID": "YOUR_LINKEDIN_CLIENT_ID",
        "LINKEDIN_CLIENT_SECRET": "YOUR_LINKEDIN_CLIENT_SECRET",
        "LINKEDIN_REDIRECT_URI": "http://127.0.0.1:8787/callback",
        "LINKEDIN_SCOPES": "openid profile email"
      }
    }
  }
}
```

If you already have other MCP servers configured, add only this object under `mcpServers`:

```json
"linkedin-jobs-connector": {
  "command": "/bin/zsh",
  "args": [
    "-lc",
    "cd '/Users/sudhendrasoanpet/Downloads/linkedin-jobs-connector' && PYTHONPATH=src python3 -m linkedin_connector.mcp_server"
  ],
  "env": {
    "LINKEDIN_CLIENT_ID": "YOUR_LINKEDIN_CLIENT_ID",
    "LINKEDIN_CLIENT_SECRET": "YOUR_LINKEDIN_CLIENT_SECRET",
    "LINKEDIN_REDIRECT_URI": "http://127.0.0.1:8787/callback",
    "LINKEDIN_SCOPES": "openid profile email"
  }
}
```

Important:

- Replace the path if your extracted folder is different.
- Use the absolute path.
- Keep `PYTHONPATH=src`.

## Step 6. Restart Claude Desktop

Quit Claude Desktop fully, then reopen it.

Open a new chat after restart so Claude reloads the MCP server list.

## Step 7. Confirm tools are available

This connector exposes these MCP tools:

- `health_check`
- `search_jobs`
- `match_connections`
- `linkedin_auth_status`
- `linkedin_begin_login`
- `linkedin_complete_login`
- `linkedin_logout`

If Claude recognizes the server, it can call these tools from chat.

## Step 8. Provide your data files

For realistic usage, prepare:

- a LinkedIn connections CSV export
- optionally a jobs JSON or CSV file if using the `file` provider

Example included files:

```text
examples/connections.csv
examples/jobs.json
```

Use absolute file paths when asking Claude to call the tools.

## Copy-paste prompts for Claude

### Prompt 0. Check LinkedIn OAuth configuration

```text
Use the linkedin-jobs-connector MCP tool linkedin_auth_status and tell me:
1. whether LinkedIn OAuth is configured
2. whether I am already authenticated
3. what limitations still apply to the available LinkedIn data
```

### Prompt 1. Start LinkedIn login

```text
Use the linkedin-jobs-connector MCP tool linkedin_begin_login and show me the auth URL.
I will open it in my browser, sign in with LinkedIn, and then paste back the full redirected callback URL.
```

### Prompt 2. Complete LinkedIn login

After you finish LinkedIn sign-in in the browser and land on the redirect URL, copy the full URL from the browser address bar and paste it into Claude using this prompt:

```text
Use the linkedin-jobs-connector MCP tool linkedin_complete_login with:
redirected_url=PASTE_THE_FULL_REDIRECTED_URL_HERE

Then confirm whether authentication succeeded and summarize the profile data returned.
```

### Prompt 3. Confirm the connector is working

```text
Use the linkedin-jobs-connector MCP tool health_check and tell me the result.
```

### Prompt 4. Demo search with bundled sample data

```text
Use the linkedin-jobs-connector MCP tool search_jobs with:
provider=demo
query=software engineer
location=Chicago
limit=50
connections_csv_path=/Users/sudhendrasoanpet/Downloads/linkedin-jobs-connector/examples/connections.csv

Then summarize:
1. the top jobs returned
2. the recruiter matches
3. the hiring manager matches
4. any 1st, 2nd, or 3rd degree connections for each job
```

### Prompt 5. Use my own jobs file

```text
Use the linkedin-jobs-connector MCP tool search_jobs with:
provider=file
query=product manager
location=Austin
limit=50
connections_csv_path=/ABSOLUTE/PATH/TO/connections.csv
jobs_file_path=/ABSOLUTE/PATH/TO/jobs.json

Then rank the jobs by best warm-introduction potential based on recruiter and hiring-manager connection strength.
```

### Prompt 6. Match connections for a specific company

```text
Use the linkedin-jobs-connector MCP tool match_connections with:
company=Acme Cloud
recruiter_name=Maya Chen
hiring_manager_name=Jordan Patel
connections_csv_path=/Users/sudhendrasoanpet/Downloads/linkedin-jobs-connector/examples/connections.csv

Then explain which connections are strongest and why.
```

## What you must do from your end

To test official LinkedIn login in Claude Desktop, you need to create and configure a LinkedIn app yourself.

You need:

1. A LinkedIn developer application
2. `Sign In with LinkedIn using OpenID Connect` enabled for that app
3. A redirect URL added to that app that exactly matches your local config
4. Your own `LINKEDIN_CLIENT_ID`
5. Your own `LINKEDIN_CLIENT_SECRET`

Populate those values in your local environment before starting Claude's MCP server.

Example:

```bash
export LINKEDIN_CLIENT_ID="YOUR_CLIENT_ID"
export LINKEDIN_CLIENT_SECRET="YOUR_CLIENT_SECRET"
export LINKEDIN_REDIRECT_URI="http://127.0.0.1:8787/callback"
export LINKEDIN_SCOPES="openid profile email"
```

Then start Claude Desktop with the MCP config pointing to that environment.

## Troubleshooting

### Claude does not show the connector

Check:

- Claude Desktop was fully restarted
- the JSON config is valid
- the folder path is correct
- `python3` works in Terminal

### The server fails to start

Run this manually:

```bash
cd /Users/sudhendrasoanpet/Downloads/linkedin-jobs-connector
PYTHONPATH=src python3 -m linkedin_connector.mcp_server
```

If that command fails, fix the local Python or path issue first.

### Claude cannot find the CSV or JSON file

Use absolute paths, not relative paths.

### I want to use claude.ai in the browser

That requires a hosted remote MCP deployment. This repository currently documents local Claude Desktop setup, not a public remote deployment.

### LinkedIn login works, but I still do not get live jobs or broad connections

That is expected with open LinkedIn permissions. Authentication and data access are different. LinkedIn sign-in proves the member identity, but the APIs for broader connections and restricted profile/job graph data require separate access approvals from LinkedIn.

## Related files

- `README.md`
- `UPLOAD_GUIDE.md`
- `connector.manifest.json`
