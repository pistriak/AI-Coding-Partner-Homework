# AI-Powered Multi-Agent Banking Transaction Pipeline

**Author**: Ruslan Pistriak

A multi-agent system that processes banking transactions through validation, fraud detection, and settlement using file-based JSON message passing.

---

## Architecture

```
sample-transactions.json
        │
        ▼
  ┌─────────────┐
  │  Integrator  │  ← loads JSON, creates shared/ dirs
  └──────┬──────┘
         │  writes to shared/input/
         ▼
  ┌──────────────────────┐
  │ Transaction Validator │  ← validates fields, amounts, currency
  └──────────┬───────────┘
             │  writes to shared/output/
             ▼
  ┌──────────────────────┐
  │    Fraud Detector     │  ← scores risk 0–10
  └──────────┬───────────┘
             │  writes to shared/output/
             ▼
  ┌──────────────────────┐
  │ Settlement Processor  │  ← settles or flags
  └──────────┬───────────┘
             │  writes to shared/results/
             ▼
      Final JSON results
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.9+ |
| Monetary math | `decimal.Decimal` (never `float`) |
| Testing | `pytest` + `pytest-cov` |
| MCP Server | FastMCP |
| Message format | JSON files in `shared/` directories |
| Logging | Python `logging` module → `pipeline.log` |

---

## Agents

### 1. Transaction Validator (`agents/transaction_validator.py`)
- Validates required fields: `transaction_id`, `amount`, `currency`, `source_account`, `destination_account`
- Validates positive `Decimal` amounts
- Validates currency against ISO 4217 whitelist (USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD)
- Rejects invalid transactions with specific reason codes

### 2. Fraud Detector (`agents/fraud_detector.py`)
- Scores transactions on a 0–10 risk scale
- Triggers: amount > $10k (+3), amount > $50k (+4 additional), unusual hour 02–05 UTC (+2), cross-border (+1)
- Risk levels: LOW (0–2), MEDIUM (3–6), HIGH (7–10)

### 3. Settlement Processor (`agents/settlement_processor.py`)
- Settles LOW/MEDIUM risk → `status: "settled"`
- Flags HIGH risk → `status: "flagged_for_review"`
- Passes through rejected transactions
- Assigns UUID4 `settlement_id` and ISO 8601 `settlement_timestamp`

---

## Sample Results (8 Transactions)

| ID | Status | Risk | Score | Reason |
|----|--------|------|-------|--------|
| TXN001 | settled | LOW | 0 | — |
| TXN002 | settled | MEDIUM | 3 | — |
| TXN003 | settled | LOW | 0 | — |
| TXN004 | settled | MEDIUM | 3 | — |
| TXN005 | flagged_for_review | HIGH | 7 | — |
| TXN006 | rejected | — | — | INVALID_CURRENCY |
| TXN007 | rejected | — | — | INVALID_AMOUNT |
| TXN008 | settled | LOW | 0 | — |

---

## Project Structure

```
homework-6/
├── agents/
│   ├── __init__.py
│   ├── transaction_validator.py   # Agent 1
│   ├── fraud_detector.py          # Agent 2
│   └── settlement_processor.py    # Agent 3
├── tests/
│   ├── __init__.py
│   ├── test_validator.py
│   ├── test_fraud_detector.py
│   ├── test_settlement.py
│   ├── test_integration.py
│   └── test_cli_and_main.py
├── mcp/
│   └── server.py                  # FastMCP pipeline-status server
├── shared/                        # File-based message passing
│   ├── input/
│   ├── processing/
│   ├── output/
│   └── results/
├── .claude/
│   ├── commands/
│   │   ├── run-pipeline.md
│   │   ├── validate-transactions.md
│   │   └── write-spec.md
│   └── settings.json              # pre-push coverage gate hook
├── integrator.py                  # Orchestrator
├── sample-transactions.json       # 8 test transactions
├── specification.md               # Full specification
├── agents.md                      # Agent descriptions
├── research-notes.md              # context7 research log
├── requirements.txt
├── mcp.json                       # MCP server config
├── HOWTORUN.md
└── README.md
```

---

## Quick Start

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the pipeline
python3 integrator.py

# Run tests with coverage
python3 -m pytest tests/ --cov=agents --cov=integrator --cov-report=term-missing

# Validate transactions only (dry-run)
python3 agents/transaction_validator.py --dry-run
```

See [HOWTORUN.md](HOWTORUN.md) for detailed instructions.

