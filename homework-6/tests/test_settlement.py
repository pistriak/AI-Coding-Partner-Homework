"""Tests for the Settlement Processor agent."""

import uuid
import pytest
from agents.settlement_processor import process_message, _mask_account


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def low_risk_transaction():
    return {
        "transaction_id": "TXN-SP-001",
        "amount": "1500.00",
        "currency": "USD",
        "source_account": "ACC-1001",
        "destination_account": "ACC-2001",
        "status": "validated",
        "fraud_risk_score": 0,
        "fraud_risk_level": "LOW",
    }


@pytest.fixture
def medium_risk_transaction():
    return {
        "transaction_id": "TXN-SP-002",
        "amount": "25000.00",
        "currency": "USD",
        "source_account": "ACC-1002",
        "destination_account": "ACC-3001",
        "status": "validated",
        "fraud_risk_score": 3,
        "fraud_risk_level": "MEDIUM",
    }


@pytest.fixture
def high_risk_transaction():
    return {
        "transaction_id": "TXN-SP-003",
        "amount": "75000.00",
        "currency": "USD",
        "source_account": "ACC-1005",
        "destination_account": "ACC-6600",
        "status": "validated",
        "fraud_risk_score": 7,
        "fraud_risk_level": "HIGH",
    }


@pytest.fixture
def rejected_transaction():
    return {
        "transaction_id": "TXN-SP-REJ",
        "status": "rejected",
        "rejection_reason": "INVALID_CURRENCY",
    }


# ---------------------------------------------------------------------------
# Settlement tests
# ---------------------------------------------------------------------------

class TestSettled:
    def test_low_risk_settled(self, low_risk_transaction):
        result = process_message(low_risk_transaction)
        assert result["status"] == "settled"

    def test_medium_risk_settled(self, medium_risk_transaction):
        result = process_message(medium_risk_transaction)
        assert result["status"] == "settled"

    def test_settled_has_settlement_id(self, low_risk_transaction):
        result = process_message(low_risk_transaction)
        assert "settlement_id" in result
        # Should be valid UUID4
        parsed = uuid.UUID(result["settlement_id"], version=4)
        assert str(parsed) == result["settlement_id"]

    def test_settled_has_timestamp(self, low_risk_transaction):
        result = process_message(low_risk_transaction)
        assert "settlement_timestamp" in result

    def test_settled_preserves_original_fields(self, low_risk_transaction):
        result = process_message(low_risk_transaction)
        assert result["transaction_id"] == "TXN-SP-001"
        assert result["amount"] == "1500.00"

    def test_source_agent_set(self, low_risk_transaction):
        result = process_message(low_risk_transaction)
        assert result["source_agent"] == "settlement_processor"


# ---------------------------------------------------------------------------
# Flagged for review tests
# ---------------------------------------------------------------------------

class TestFlaggedForReview:
    def test_high_risk_flagged(self, high_risk_transaction):
        result = process_message(high_risk_transaction)
        assert result["status"] == "flagged_for_review"

    def test_flagged_has_settlement_id(self, high_risk_transaction):
        result = process_message(high_risk_transaction)
        assert "settlement_id" in result
        uuid.UUID(result["settlement_id"], version=4)

    def test_flagged_has_timestamp(self, high_risk_transaction):
        result = process_message(high_risk_transaction)
        assert "settlement_timestamp" in result


# ---------------------------------------------------------------------------
# Rejected passthrough tests
# ---------------------------------------------------------------------------

class TestRejectedPassthrough:
    def test_rejected_stays_rejected(self, rejected_transaction):
        result = process_message(rejected_transaction)
        assert result["status"] == "rejected"

    def test_rejected_no_settlement_id(self, rejected_transaction):
        result = process_message(rejected_transaction)
        assert "settlement_id" not in result

    def test_rejected_has_timestamp(self, rejected_transaction):
        result = process_message(rejected_transaction)
        assert "settlement_timestamp" in result

    def test_rejected_preserves_reason(self, rejected_transaction):
        result = process_message(rejected_transaction)
        assert result["rejection_reason"] == "INVALID_CURRENCY"

    def test_rejected_sets_source_agent(self, rejected_transaction):
        result = process_message(rejected_transaction)
        assert result["source_agent"] == "settlement_processor"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_missing_risk_level_defaults_settled(self):
        """Transaction with no risk level should default to settled."""
        txn = {
            "transaction_id": "TXN-EDGE",
            "amount": "100.00",
            "currency": "USD",
            "source_account": "ACC-0001",
            "destination_account": "ACC-0002",
            "status": "validated",
        }
        result = process_message(txn)
        assert result["status"] == "settled"

    def test_unique_settlement_ids(self, low_risk_transaction):
        """Each call should produce a unique settlement ID."""
        r1 = process_message(low_risk_transaction)
        r2 = process_message(low_risk_transaction)
        assert r1["settlement_id"] != r2["settlement_id"]


class TestMaskAccount:
    def test_masks_account(self):
        assert _mask_account("ACC-1001") == "ACC-***1"

