# Homework 5 - MCP Servers

Author: Ruslan Pistriak

This repository contains the implementation for Homework 5:
- External MCP servers configured: GitHub, Filesystem, Jira
- Custom MCP server built with FastMCP in `custom-mcp-server/server.py`
- Reproducible setup and run instructions in `HOWTORUN.md`
- Screenshot evidence stored in `docs/screenshots/`

## Deliverables

- `mcp.json` with server configuration template (GitHub, Filesystem, Jira, custom)
- `custom-mcp-server/server.py` with:
  - Resource URI returning content from `lorem-ipsum.md`
  - Optional `word_count` parameter (default `30`)
  - `read` tool returning the same word-limited content
- `custom-mcp-server/requirements.txt` including `fastmcp`
- `HOWTORUN.md` with install, run, connect, and usage instructions