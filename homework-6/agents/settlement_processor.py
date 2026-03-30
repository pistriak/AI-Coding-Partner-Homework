"""
Settlement Processor Agent
Settles or flags transactions based on fraud risk level.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("settlement_processor")


def _mask_account(account: str) -> str:
    """Mask account number for logging."""
    if len(account) <= 1:
        return "***"
    return account[: account.rfind("-") + 1] + "***" + account[-1]


def process_message(message: dict) -> dict:
    """
    Settle a fraud-scored transaction.

    Rules:
      - LOW / MEDIUM risk → status: "settled"
      - HIGH risk → status: "flagged_for_review"
      - Rejected transactions → passed through with status: "rejected"

    All non-rejected transactions receive:
      - settlement_id (UUID4)
      - settlement_timestamp (ISO 8601)
    """
    txn_id = message.get("transaction_id", "UNKNOWN")
    result = dict(message)

    # Pass through rejected transactions
    if message.get("status") == "rejected":
        result["source_agent"] = "settlement_processor"
        result["settlement_timestamp"] = datetime.now(timezone.utc).isoformat()
        logger.info("Passing through rejected transaction %s", txn_id)
        return result

    risk_level = message.get("fraud_risk_level", "LOW")
    settlement_id = str(uuid.uuid4())
    settlement_ts = datetime.now(timezone.utc).isoformat()

    result["settlement_id"] = settlement_id
    result["settlement_timestamp"] = settlement_ts
    result["source_agent"] = "settlement_processor"

    if risk_level == "HIGH":
        result["status"] = "flagged_for_review"
        logger.warning(
            "Flagged %s for review — HIGH risk (score=%s), settlement=%s",
            txn_id,
            message.get("fraud_risk_score", "?"),
            settlement_id,
        )
    else:
        result["status"] = "settled"
        logger.info(
            "Settled %s — %s risk (score=%s), settlement=%s",
            txn_id,
            risk_level,
            message.get("fraud_risk_score", "?"),
            settlement_id,
        )

    return result

