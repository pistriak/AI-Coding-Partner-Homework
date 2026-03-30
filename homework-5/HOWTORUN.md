# How To Run

## 1) Install dependencies

```bash
cd "/Users/Ruslan Pistriak/Desktop/AI-Coding-Partner-Homework/homework-5/custom-mcp-server"
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 2) Run the custom MCP server

```bash
cd "/Users/Ruslan Pistriak/Desktop/AI-Coding-Partner-Homework/homework-5/custom-mcp-server"
source .venv/bin/activate
python server.py
```

## 3) Run local smoke test for word-limit behavior

```bash
cd "/Users/Ruslan Pistriak/Desktop/AI-Coding-Partner-Homework/homework-5/custom-mcp-server"
source .venv/bin/activate
python smoke_test.py
```

## 4) Connect MCP configuration

Use `mcp.json` in the repo root (or copy values into your client-specific MCP settings).

- `custom-lorem` points to `custom-mcp-server/server.py`
- `github`, `filesystem`, `jira` entries are templates; update env values/paths for your machine and accounts

## 5) Use and test the `read` tool

In your MCP client, call tool `read`:
- without arguments -> returns first 30 words
- with `word_count` set (for example `10`) -> returns first 10 words

FastMCP requires Python 3.10+, and these steps were validated with Python 3.12.

## 6) Capture screenshots for submission

Save screenshots in `docs/screenshots/`:
- GitHub MCP call result
- Filesystem MCP call result
- Jira request and response for last 5 bugs (ticket keys only)
- Custom MCP `read` tool result

