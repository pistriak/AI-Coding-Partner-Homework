"""
Fraud Detector Agent
Scores validated transactions for fraud risk on a 0–10 scale.
"""

import decimal
import logging
from datetime import datetime, timezone

logger = logging.getLogger("fraud_detector")


def _mask_account(account: str) -> str:
    """Mask account number for logging."""
    if len(account) <= 1:
        return "***"
    return account[: account.rfind("-") + 1] + "***" + account[-1]


def _get_risk_level(score: int) -> str:
    """Map numeric score to risk level string."""
    if score <= 2:
        return "LOW"
    elif score <= 6:
        return "MEDIUM"
    else:
        return "HIGH"


def process_message(message: dict) -> dict:
    """
    Score a validated transaction for fraud risk.

    Scoring rules:
      - Amount > $10,000  → +3 points
      - Amount > $50,000  → +4 points (additional, cumulative with above)
      - Unusual hour (02:00–05:00 UTC) → +2 points
      - Cross-border (country ≠ 'US') → +1 point

    Risk levels:
      - 0–2: LOW
      - 3–6: MEDIUM
      - 7–10: HIGH

    Rejected transactions are passed through unchanged.
    """
    txn_id = message.get("transaction_id", "UNKNOWN")
    result = dict(message)

    # Pass through rejected transactions
    if message.get("status") == "rejected":
        result["source_agent"] = "fraud_detector"
        result["target_agent"] = "settlement_processor"
        logger.info("Skipping rejected transaction %s", txn_id)
        return result

    score = 0
    triggers = []

    # --- Amount-based scoring ---
    try:
        amount = decimal.Decimal(str(message.get("amount", "0")))
    except (decimal.InvalidOperation, ValueError, TypeError):
        amount = decimal.Decimal("0")

    if amount > decimal.Decimal("10000"):
        score += 3
        triggers.append("amount>10k(+3)")

    if amount > decimal.Decimal("50000"):
        score += 4
        triggers.append("amount>50k(+4)")

    # --- Unusual-hour scoring ---
    timestamp_str = message.get("timestamp", "")
    if timestamp_str:
        try:
            ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            hour = ts.hour
            if 2 <= hour < 5:
                score += 2
                triggers.append(f"unusual_hour({hour}:00,+2)")
        except (ValueError, TypeError):
            pass

    # --- Cross-border scoring ---
    metadata = message.get("metadata", {})
    country = metadata.get("country", "US")
    if country != "US":
        score += 1
        triggers.append(f"cross_border({country},+1)")

    # Cap at 10
    score = min(score, 10)
    risk_level = _get_risk_level(score)

    result["fraud_risk_score"] = score
    result["fraud_risk_level"] = risk_level
    result["fraud_triggers"] = triggers
    result["fraud_scored_at"] = datetime.now(timezone.utc).isoformat()
    result["source_agent"] = "fraud_detector"
    result["target_agent"] = "settlement_processor"

    logger.info(
        "Scored %s — risk=%d (%s) triggers=%s",
        txn_id,
        score,
        risk_level,
        triggers,
    )

    return result

