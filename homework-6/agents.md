# Agents — AI-Powered Multi-Agent Banking Pipeline

## Project Context

This project implements a multi-agent banking transaction processing pipeline.
Eight sample transactions from `sample-transactions.json` flow through three
cooperating agents via file-based JSON message passing in `shared/` directories.

**Tech Stack**: Python 3.10+, decimal.Decimal, FastMCP, pytest + pytest-cov

---

## Agent 1 — Transaction Validator

| Property | Value |
|----------|-------|
| **File** | `agents/transaction_validator.py` |
| **Entry point** | `process_message(message: dict) -> dict` |
| **Reads from** | `shared/input/` |
| **Writes to** | `shared/processing/` → `shared/output/` |
| **Purpose** | Validates required fields, positive amounts, and ISO 4217 currency codes |

### Validation rules
- Required fields: `transaction_id`, `amount`, `currency`, `source_account`, `destination_account`
- `amount` must parse as a positive `decimal.Decimal`
- `currency` must be in: USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD
- Rejected transactions get `status: "rejected"` and a `rejection_reason`

---

## Agent 2 — Fraud Detector

| Property | Value |
|----------|-------|
| **File** | `agents/fraud_detector.py` |
| **Entry point** | `process_message(message: dict) -> dict` |
| **Reads from** | `shared/output/` (validator results) |
| **Writes to** | `shared/processing/` → `shared/output/` |
| **Purpose** | Scores validated transactions for fraud risk on a 0–10 scale |

### Scoring rules
| Trigger | Points |
|---------|--------|
| Amount > $10,000 | +3 |
| Amount > $50,000 | +4 (additional) |
| Unusual hour (02:00–05:00 UTC) | +2 |
| Cross-border (country ≠ US) | +1 |

### Risk levels
| Score | Level |
|-------|-------|
| 0–2 | LOW |
| 3–6 | MEDIUM |
| 7–10 | HIGH |

---

## Agent 3 — Settlement Processor

| Property | Value |
|----------|-------|
| **File** | `agents/settlement_processor.py` |
| **Entry point** | `process_message(message: dict) -> dict` |
| **Reads from** | `shared/output/` (fraud-scored results) |
| **Writes to** | `shared/results/` |
| **Purpose** | Settles or flags transactions based on risk level |

### Settlement rules
- LOW / MEDIUM risk → `status: "settled"`, assigned `settlement_id` (UUID4) and `settlement_timestamp`
- HIGH risk → `status: "flagged_for_review"`, assigned `settlement_id` and `settlement_timestamp`
- Rejected transactions → passed through with `status: "rejected"`

---

## Integrator / Orchestrator

| Property | Value |
|----------|-------|
| **File** | `integrator.py` |
| **Purpose** | Sets up `shared/` directories, loads transactions, runs agents in sequence, reports results |

### Flow
```
sample-transactions.json
        │
        ▼
  ┌─────────────┐
  │  Integrator  │  ← loads JSON, creates shared/ dirs
  └──────┬──────┘
         │  writes to shared/input/
         ▼
  ┌─────────────────────┐
  │ Transaction Validator│  ← validates fields, amounts, currency
  └──────────┬──────────┘
             │  writes to shared/output/
             ▼
  ┌─────────────────────┐
  │   Fraud Detector     │  ← scores risk 0–10
  └──────────┬──────────┘
             │  writes to shared/output/
             ▼
  ┌─────────────────────┐
  │ Settlement Processor │  ← settles or flags
  └──────────┬──────────┘
             │  writes to shared/results/
             ▼
     Final JSON results
```

