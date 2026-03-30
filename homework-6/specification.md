# Specification: AI-Powered Multi-Agent Banking Transaction Pipeline

## 1. High-Level Objective

Build a 3-agent Python pipeline that validates, scores for fraud risk, and settles banking transactions using file-based JSON message passing through shared directories.

## 2. Mid-Level Objectives

- Transactions with invalid or missing required fields are rejected by the Transaction Validator with a specific reason (e.g. `INVALID_CURRENCY`, `MISSING_FIELD`, `INVALID_AMOUNT`).
- Transactions above $10,000 are assigned `fraud_risk_level: "HIGH"` by the Fraud Detector using a cumulative scoring system (0–10 scale).
- Transactions occurring between 02:00–05:00 UTC receive +2 fraud risk points for unusual timing.
- All validated and risk-scored transactions are settled by the Settlement Processor, which writes final results (with settlement ID and timestamp) to `shared/results/`.
- The pipeline processes all 8 sample transactions end-to-end and produces 8 result files in `shared/results/`, each containing the full processing history.

## 3. Implementation Notes

- **Monetary calculations**: Use `decimal.Decimal` exclusively — never `float`.
- **Currency validation**: ISO 4217 whitelist: `USD`, `EUR`, `GBP`, `JPY`, `CHF`, `CAD`, `AUD`, `NZD`.
- **Logging**: Audit trail with ISO 8601 timestamp, agent name, transaction_id, and outcome. Written to `pipeline.log`.
- **PII**: Mask account numbers in all log output (e.g. `ACC-***1`).
- **Message IDs**: UUID4 for every inter-agent message.
- **Error handling**: Agents must never crash on bad input — always return a structured rejection.
- **Idempotency**: Re-running the pipeline on the same input produces identical results.

## 4. Context

- **Beginning state**: `sample-transactions.json` exists with 8 raw transaction records. No agents exist. No `shared/` directories exist.
- **Ending state**: All 8 transactions processed. Results in `shared/results/`. Test coverage ≥ 90%. `README.md` and `HOWTORUN.md` complete. Pipeline is queryable via MCP server.

## 5. Low-Level Tasks

### Task: Transaction Validator

**Prompt**: "Create a Python module `agents/transaction_validator.py` that validates banking transactions. It must expose a `process_message(message: dict) -> dict` function. Validate these required fields: transaction_id, amount, currency, source_account, destination_account. Amount must be a positive Decimal. Currency must be in the ISO 4217 whitelist (USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD). On success, return the message with `status: 'validated'`. On failure, return `status: 'rejected'` with a `rejection_reason` field. Support `--dry-run` CLI mode that validates all transactions from sample-transactions.json and prints a summary table. Use decimal.Decimal for amounts, never float. Mask account numbers in logs."

**File to CREATE**: `agents/transaction_validator.py`
**Function to CREATE**: `process_message(message: dict) -> dict`
**Details**:
- Check required fields: `transaction_id`, `amount`, `currency`, `source_account`, `destination_account`
- Validate amount is a positive `Decimal`
- Validate currency against ISO 4217 whitelist
- Return message with `status: "validated"` or `status: "rejected"` + `rejection_reason` field
- Support `--dry-run` CLI flag for standalone validation

### Task: Fraud Detector

**Prompt**: "Create a Python module `agents/fraud_detector.py` that scores validated banking transactions for fraud risk. It must expose a `process_message(message: dict) -> dict` function. Use a cumulative point system (0–10): amount > $10,000 → +3 pts; amount > $50,000 → +4 pts (additional); unusual hour 02:00–05:00 UTC → +2 pts; cross-border (country ≠ 'US') → +1 pt. Risk levels: LOW (0–2), MEDIUM (3–6), HIGH (7–10). Add `fraud_risk_score` and `fraud_risk_level` fields to the message. Skip rejected transactions. Use decimal.Decimal for amount comparisons. Log all scoring decisions."

**File to CREATE**: `agents/fraud_detector.py`
**Function to CREATE**: `process_message(message: dict) -> dict`
**Details**:
- Score transaction for fraud risk on 0–10 scale
- Scoring triggers: amount > $10,000 (+3), amount > $50,000 (+4 additional), unusual hour 02:00–05:00 UTC (+2), cross-border (+1)
- Risk levels: LOW (0–2), MEDIUM (3–6), HIGH (7–10)
- Return message with `fraud_risk_score` and `fraud_risk_level` fields
- Pass through rejected transactions unchanged

### Task: Settlement Processor

**Prompt**: "Create a Python module `agents/settlement_processor.py` that settles validated and risk-scored banking transactions. It must expose a `process_message(message: dict) -> dict` function. For validated transactions: generate a settlement_id (UUID4), add settlement_timestamp (ISO 8601), set status to 'settled' for LOW/MEDIUM risk or 'flagged_for_review' for HIGH risk. For rejected transactions: set status to 'rejected' and pass through. Write final results as JSON files to shared/results/. Use decimal.Decimal. Log all settlement actions."

**File to CREATE**: `agents/settlement_processor.py`
**Function to CREATE**: `process_message(message: dict) -> dict`
**Details**:
- Generate `settlement_id` (UUID4) and `settlement_timestamp` (ISO 8601)
- Set final status: `"settled"` for LOW/MEDIUM risk, `"flagged_for_review"` for HIGH risk
- Pass through rejected transactions with `status: "rejected"`
- Write each result as a JSON file in `shared/results/`

