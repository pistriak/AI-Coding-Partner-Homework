#!/usr/bin/env python3
"""
Custom FastMCP server for the banking transaction pipeline.

Exposes:
  - Tool: get_transaction_status(transaction_id) — returns status from shared/results/
  - Tool: list_pipeline_results() — returns summary of all processed transactions
  - Resource: pipeline://summary — latest pipeline run summary as text
"""

import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pipeline-status")

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "shared" / "results"


def _load_result(filepath: Path) -> dict:
    """Load a single result JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_all_results() -> list:
    """Load all result files from shared/results/."""
    results = []
    if not RESULTS_DIR.exists():
        return results
    for fp in sorted(RESULTS_DIR.glob("*.json")):
        try:
            results.append(_load_result(fp))
        except (json.JSONDecodeError, OSError):
            continue
    return results


@mcp.tool()
def get_transaction_status(transaction_id: str) -> str:
    """
    Get the current status of a transaction by its ID.

    Args:
        transaction_id: The transaction ID (e.g. "TXN001")

    Returns:
        JSON string with the transaction's current status and details.
    """
    filename = f"{transaction_id}.json"
    filepath = RESULTS_DIR / filename

    if not filepath.exists():
        return json.dumps({"error": f"Transaction {transaction_id} not found in results"})

    result = _load_result(filepath)
    data = result.get("data", {})

    return json.dumps(
        {
            "transaction_id": data.get("transaction_id"),
            "status": data.get("status"),
            "fraud_risk_level": data.get("fraud_risk_level"),
            "fraud_risk_score": data.get("fraud_risk_score"),
            "settlement_id": data.get("settlement_id"),
            "rejection_reason": data.get("rejection_reason"),
        },
        indent=2,
    )


@mcp.tool()
def list_pipeline_results() -> str:
    """
    List a summary of all processed transactions.

    Returns:
        JSON string with an array of transaction summaries.
    """
    results = _load_all_results()

    if not results:
        return json.dumps({"message": "No results found. Run the pipeline first."})

    summaries = []
    for r in results:
        data = r.get("data", {})
        summaries.append(
            {
                "transaction_id": data.get("transaction_id"),
                "status": data.get("status"),
                "fraud_risk_level": data.get("fraud_risk_level"),
                "fraud_risk_score": data.get("fraud_risk_score"),
                "amount": data.get("amount"),
                "currency": data.get("currency"),
            }
        )

    return json.dumps(summaries, indent=2)


@mcp.resource("pipeline://summary")
def pipeline_summary() -> str:
    """Return the latest pipeline run summary as text."""
    results = _load_all_results()

    if not results:
        return "No pipeline results found. Run the pipeline first with: python3 integrator.py"

    settled = 0
    flagged = 0
    rejected = 0

    lines = ["Pipeline Results Summary", "=" * 60]

    for r in results:
        data = r.get("data", {})
        txn_id = data.get("transaction_id", "N/A")
        status = data.get("status", "unknown")
        risk = data.get("fraud_risk_level", "—")
        score = data.get("fraud_risk_score", "—")

        if status == "settled":
            settled += 1
        elif status == "flagged_for_review":
            flagged += 1
        elif status == "rejected":
            rejected += 1

        lines.append(f"  {txn_id}: {status} (risk={risk}, score={score})")

    lines.append("=" * 60)
    lines.append(f"Settled: {settled} | Flagged: {flagged} | Rejected: {rejected} | Total: {len(results)}")

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()

