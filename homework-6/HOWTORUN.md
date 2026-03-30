# How To Run

## Prerequisites

- Python 3.9 or higher
- pip3

## 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

This installs:
- `pytest` — test framework
- `pytest-cov` — coverage plugin
- `mcp[cli]` — FastMCP for the pipeline-status MCP server

## 2. Run the Pipeline

```bash
python3 integrator.py
```

This will:
1. Create/reset `shared/` directories (input, processing, output, results)
2. Load 8 transactions from `sample-transactions.json`
3. Run each transaction through: Validator → Fraud Detector → Settlement Processor
4. Write results to `shared/results/` as individual JSON files
5. Print a summary table to the console
6. Write a full audit log to `pipeline.log`

### Expected Output

```
  Settled: 5  |  Flagged: 1  |  Rejected: 2  |  Total: 8
```

## 3. Validate Transactions Only (Dry Run)

```bash
python3 agents/transaction_validator.py --dry-run
```

This validates all transactions without running the full pipeline.

## 4. Run Tests

```bash
# Full test suite with coverage
python3 -m pytest tests/ --cov=agents --cov=integrator --cov-report=term-missing -v

# Quick run (no verbose)
python3 -m pytest tests/ -q

# With coverage threshold check
python3 -m pytest tests/ --cov=agents --cov=integrator --cov-fail-under=90
```

### Expected Test Results

- **90 tests passing**
- **96% code coverage** (target ≥ 90%)

## 5. MCP Server

### Start the pipeline-status MCP server:

```bash
python3 mcp/server.py
```

### Available Tools

| Tool | Description |
|------|-------------|
| `get_transaction_status(transaction_id)` | Get status of a single transaction |
| `list_pipeline_results()` | List all processed transactions |

### Available Resources

| URI | Description |
|-----|-------------|
| `pipeline://summary` | Latest pipeline run summary text |

### MCP Configuration

The `mcp.json` file configures two MCP servers:
- **context7** — Library documentation lookup
- **pipeline-status** — Custom pipeline query server

## 6. Project Files

| File | Purpose |
|------|---------|
| `integrator.py` | Orchestrator — runs the full pipeline |
| `agents/transaction_validator.py` | Agent 1 — validates fields, amounts, currency |
| `agents/fraud_detector.py` | Agent 2 — scores fraud risk 0–10 |
| `agents/settlement_processor.py` | Agent 3 — settles or flags transactions |
| `mcp/server.py` | FastMCP pipeline-status server |
| `pipeline.log` | Audit log from latest run |
| `shared/results/*.json` | Final results (one per transaction) |

## 7. Troubleshooting

- **`python3: command not found`** — Install Python from python.org or via `brew install python3`
- **Import errors** — Run from the project root directory (`homework-6/`)
- **MCP server won't start** — Ensure `mcp[cli]` is installed: `pip3 install "mcp[cli]"`
- **Coverage below threshold** — Run `python3 -m pytest tests/ --cov=agents --cov=integrator --cov-report=term-missing` to see which lines are uncovered

