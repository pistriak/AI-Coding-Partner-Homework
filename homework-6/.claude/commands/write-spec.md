Generate a detailed technical specification for the multi-agent banking transaction pipeline.

Context:
- The project processes banking transactions from `sample-transactions.json` through 3 cooperating agents
- Agents communicate via file-based JSON message passing in `shared/` directories
- Tech stack: Python 3.10+, decimal.Decimal, pytest, FastMCP

Task:
Using the template in `specification-TEMPLATE-hint.md`, produce a complete `specification.md` with all 5 sections:

1. **High-Level Objective** — One sentence describing the pipeline
2. **Mid-Level Objectives** — 4–5 concrete, testable requirements
3. **Implementation Notes** — Constraints (Decimal, ISO 4217, logging, PII masking)
4. **Context** — Beginning and ending state
5. **Low-Level Tasks** — One entry per agent with: Task name, exact Prompt, File to CREATE, Function to CREATE, and Details

Agents to specify:
- Transaction Validator (`agents/transaction_validator.py`) — validates fields, amounts, ISO 4217 currency
- Fraud Detector (`agents/fraud_detector.py`) — scores risk 0–10, assigns LOW/MEDIUM/HIGH
- Settlement Processor (`agents/settlement_processor.py`) — settles or flags based on risk

Rules:
- Monetary values use `decimal.Decimal`, never `float`
- Currency whitelist: USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD
- All logs use ISO 8601 timestamps and mask account numbers
- Each Low-Level Task prompt must be specific enough to generate production-quality code

Output:
Write the specification to `specification.md` in the project root.

