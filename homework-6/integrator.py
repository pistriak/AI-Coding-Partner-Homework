#!/usr/bin/env python3
"""
Integrator / Orchestrator
Sets up shared/ directories, loads transactions from sample-transactions.json,
runs the three agents in sequence, and reports results.
"""

import json
import logging
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from agents.transaction_validator import process_message as validate
from agents.fraud_detector import process_message as detect_fraud
from agents.settlement_processor import process_message as settle

BASE_DIR = Path(__file__).resolve().parent
SHARED_DIR = BASE_DIR / "shared"
INPUT_DIR = SHARED_DIR / "input"
PROCESSING_DIR = SHARED_DIR / "processing"
OUTPUT_DIR = SHARED_DIR / "output"
RESULTS_DIR = SHARED_DIR / "results"

LOG_FILE = BASE_DIR / "pipeline.log"


def _setup_logging() -> None:
    """Configure logging to file and console."""
    fmt = "%(asctime)s [%(name)s] %(levelname)s — %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=fmt,
        handlers=[
            logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def _setup_directories() -> None:
    """Create (or reset) shared/ directories."""
    for d in (INPUT_DIR, PROCESSING_DIR, OUTPUT_DIR, RESULTS_DIR):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)


def _write_json(directory: Path, filename: str, data: dict) -> Path:
    """Write a dict as pretty JSON to a file."""
    path = directory / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    return path


def _wrap_message(
    data: dict,
    source_agent: str,
    target_agent: str,
    message_type: str = "transaction",
) -> dict:
    """Wrap raw transaction data into the standard message envelope."""
    return {
        "message_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_agent": source_agent,
        "target_agent": target_agent,
        "message_type": message_type,
        "data": data,
    }


def run_pipeline(transactions_path: Optional[str] = None) -> List[Dict]:
    """
    Run the full pipeline:
      1. Load transactions
      2. Write to shared/input/
      3. Transaction Validator → shared/output/
      4. Fraud Detector → shared/output/ (overwrites)
      5. Settlement Processor → shared/results/
      6. Report summary
    """
    logger = logging.getLogger("integrator")

    if transactions_path is None:
        transactions_path = str(BASE_DIR / "sample-transactions.json")

    # Load transactions
    with open(transactions_path, "r", encoding="utf-8") as f:
        transactions = json.load(f)

    logger.info("Loaded %d transactions from %s", len(transactions), transactions_path)

    final_results: List[Dict] = []

    for txn in transactions:
        txn_id = txn.get("transaction_id", "UNKNOWN")
        filename = f"{txn_id}.json"

        # Step 1: Write raw transaction to shared/input/
        msg = _wrap_message(txn, "integrator", "transaction_validator")
        _write_json(INPUT_DIR, filename, msg)
        logger.info("→ Input: %s", txn_id)

        # Step 2: Transaction Validator
        _write_json(PROCESSING_DIR, filename, msg)
        validated = validate(txn)
        out_msg = _wrap_message(validated, "transaction_validator", "fraud_detector")
        _write_json(OUTPUT_DIR, filename, out_msg)
        logger.info("→ Validated: %s — %s", txn_id, validated.get("status"))

        # Step 3: Fraud Detector
        _write_json(PROCESSING_DIR, filename, out_msg)
        scored = detect_fraud(validated)
        out_msg = _wrap_message(scored, "fraud_detector", "settlement_processor")
        _write_json(OUTPUT_DIR, filename, out_msg)
        if scored.get("status") != "rejected":
            logger.info(
                "→ Scored: %s — risk=%s (%s)",
                txn_id,
                scored.get("fraud_risk_score"),
                scored.get("fraud_risk_level"),
            )

        # Step 4: Settlement Processor
        _write_json(PROCESSING_DIR, filename, out_msg)
        settled = settle(scored)
        result_msg = _wrap_message(settled, "settlement_processor", "results")
        _write_json(RESULTS_DIR, filename, result_msg)
        logger.info("→ Result: %s — %s", txn_id, settled.get("status"))

        final_results.append(result_msg)

    return final_results


def print_summary(results: List[Dict]) -> None:
    """Print a summary table of pipeline results."""
    print(f"\n{'='*72}")
    print("  Pipeline Results Summary")
    print(f"{'='*72}")
    print(f"  {'ID':<10} {'Status':<22} {'Risk':<8} {'Score':<6} {'Reason'}")
    print(f"  {'-'*10} {'-'*22} {'-'*8} {'-'*6} {'-'*20}")

    settled = 0
    flagged = 0
    rejected = 0

    for r in results:
        data = r.get("data", {})
        txn_id = data.get("transaction_id", "N/A")
        status = data.get("status", "unknown")
        risk = data.get("fraud_risk_level", "—")
        score = data.get("fraud_risk_score", "—")
        reason = data.get("rejection_reason", "—")

        if status == "settled":
            settled += 1
        elif status == "flagged_for_review":
            flagged += 1
        elif status == "rejected":
            rejected += 1

        print(f"  {txn_id:<10} {status:<22} {str(risk):<8} {str(score):<6} {reason}")

    print(f"{'='*72}")
    print(f"  Settled: {settled}  |  Flagged: {flagged}  |  Rejected: {rejected}  |  Total: {len(results)}")
    print(f"{'='*72}\n")


def main() -> None:
    _setup_logging()
    logger = logging.getLogger("integrator")
    logger.info("Starting multi-agent banking pipeline")

    _setup_directories()
    results = run_pipeline()
    print_summary(results)

    logger.info("Pipeline complete — %d results written to %s", len(results), RESULTS_DIR)


if __name__ == "__main__":
    main()

