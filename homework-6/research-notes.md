# Research Notes — context7 Queries

This document records context7 MCP queries made during pipeline development (Agent 2 — Code Generation).

---

## Query 1: Python decimal module for monetary arithmetic

- **Search**: "Python decimal module"
- **context7 library ID**: `/python/cpython`
- **Key insight**: Used `decimal.Decimal(str(value))` for safe conversion from JSON string amounts. Applied `ROUND_HALF_UP` awareness for consistent rounding behavior. Confirmed that `Decimal` comparisons work naturally with `>` operator, so `Decimal("10000")` comparisons in the fraud detector are straightforward. Never use `float` for monetary values — `Decimal` avoids IEEE 754 floating-point rounding errors.
- **Applied**: All three agents use `decimal.Decimal` for amount parsing and comparison. The Transaction Validator parses amounts with `decimal.Decimal(str(message["amount"]))` and validates positivity. The Fraud Detector compares against `Decimal("10000")` and `Decimal("50000")` thresholds.

---

## Query 2: FastMCP Python framework for building MCP servers

- **Search**: "FastMCP Python MCP server"
- **context7 library ID**: `/jlowin/fastmcp`
- **Key insight**: FastMCP provides a decorator-based API for defining tools and resources. Tools are defined with `@mcp.tool()` and resources with `@mcp.resource("uri://pattern")`. The `FastMCP("name")` constructor creates a server instance, and `mcp.run()` starts it. Parameters are declared as function arguments with type hints — FastMCP auto-generates the JSON schema for the MCP protocol.
- **Applied**: Built `mcp/server.py` with two tools (`get_transaction_status`, `list_pipeline_results`) and one resource (`pipeline://summary`). Used the decorator pattern discovered via context7 for clean, minimal server code.

---

## Query 3: pytest temporary directory fixtures

- **Search**: "pytest tmp_path fixture"
- **context7 library ID**: `/pytest-dev/pytest`
- **Key insight**: The `tmp_path` fixture provides a unique temporary directory (`pathlib.Path`) per test invocation, automatically cleaned up. This isolates test runs from the real `shared/` directory. Combined with `monkeypatch` to redirect agent file operations to temp directories during testing.
- **Applied**: All integration tests use `tmp_path` to create isolated `shared/` directory trees, ensuring tests don't interfere with each other or with production data.

