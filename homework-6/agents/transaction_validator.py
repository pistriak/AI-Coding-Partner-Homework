"""
Transaction Validator Agent
Validates required fields, positive amounts, and ISO 4217 currency codes.
"""

import decimal
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger("transaction_validator")

REQUIRED_FIELDS = [
    "transaction_id",
    "amount",
    "currency",
    "source_account",
    "destination_account",
]

VALID_CURRENCIES = {"USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD"}


def _mask_account(account: str) -> str:
    """Mask account number for logging, showing only last character."""
    if len(account) <= 1:
        return "***"
    return account[: account.rfind("-") + 1] + "***" + account[-1]


def process_message(message: dict) -> dict:
    """
    Validate a transaction message.

    Returns the message enriched with:
      - status: "validated" | "rejected"
      - rejection_reason (if rejected)
      - validated_at timestamp
      - source_agent / target_agent metadata
    """
    txn_id = message.get("transaction_id", "UNKNOWN")
    result = dict(message)

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in message or message[field] is None or str(message[field]).strip() == "":
            result["status"] = "rejected"
            result["rejection_reason"] = f"MISSING_FIELD:{field}"
            logger.warning(
                "Rejected %s — missing field: %s",
                txn_id,
                field,
            )
            return result

    # Validate amount is a positive Decimal
    try:
        amount = decimal.Decimal(str(message["amount"]))
    except (decimal.InvalidOperation, ValueError, TypeError):
        result["status"] = "rejected"
        result["rejection_reason"] = "INVALID_AMOUNT"
        logger.warning("Rejected %s — amount is not a valid number", txn_id)
        return result

    if amount <= 0:
        result["status"] = "rejected"
        result["rejection_reason"] = "INVALID_AMOUNT"
        logger.warning("Rejected %s — amount must be positive, got %s", txn_id, amount)
        return result

    # Validate currency
    currency = str(message["currency"]).upper()
    if currency not in VALID_CURRENCIES:
        result["status"] = "rejected"
        result["rejection_reason"] = "INVALID_CURRENCY"
        logger.warning("Rejected %s — invalid currency: %s", txn_id, currency)
        return result

    # All checks passed
    result["status"] = "validated"
    result["validated_at"] = datetime.now(timezone.utc).isoformat()
    result["source_agent"] = "transaction_validator"
    result["target_agent"] = "fraud_detector"

    logger.info(
        "Validated %s — %s %s from %s to %s",
        txn_id,
        amount,
        currency,
        _mask_account(message["source_account"]),
        _mask_account(message["destination_account"]),
    )

    return result


def dry_run(transactions_path: str = "sample-transactions.json") -> None:
    """Validate all transactions and print a summary table."""
    with open(transactions_path, "r") as f:
        transactions = json.load(f)

    valid_count = 0
    invalid_count = 0
    results = []

    for txn in transactions:
        result = process_message(txn)
        status = result.get("status", "unknown")
        reason = result.get("rejection_reason", "—")
        if status == "validated":
            valid_count += 1
        else:
            invalid_count += 1
        results.append(
            {
                "transaction_id": txn.get("transaction_id", "N/A"),
                "status": status,
                "reason": reason,
            }
        )

    total = len(transactions)
    print(f"\n{'='*60}")
    print(f"  Transaction Validation Summary (Dry Run)")
    print(f"{'='*60}")
    print(f"  Total: {total}  |  Valid: {valid_count}  |  Invalid: {invalid_count}")
    print(f"{'='*60}")
    print(f"  {'ID':<12} {'Status':<14} {'Reason'}")
    print(f"  {'-'*12} {'-'*14} {'-'*30}")
    for r in results:
        print(f"  {r['transaction_id']:<12} {r['status']:<14} {r['reason']}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
    if "--dry-run" in sys.argv:
        path = "sample-transactions.json"
        for i, arg in enumerate(sys.argv):
            if arg == "--file" and i + 1 < len(sys.argv):
                path = sys.argv[i + 1]
        dry_run(path)

