"""Tests for the Fraud Detector agent."""

import decimal
import pytest
from agents.fraud_detector import process_message, _get_risk_level, _mask_account


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def validated_transaction():
    """Return a validated transaction ready for fraud scoring."""
    return {
        "transaction_id": "TXN-FD-001",
        "amount": "1500.00",
        "currency": "USD",
        "source_account": "ACC-1001",
        "destination_account": "ACC-2001",
        "timestamp": "2026-03-16T09:00:00Z",
        "transaction_type": "transfer",
        "status": "validated",
        "metadata": {"channel": "online", "country": "US"},
    }


@pytest.fixture
def rejected_transaction():
    """Return a rejected transaction."""
    return {
        "transaction_id": "TXN-FD-REJ",
        "status": "rejected",
        "rejection_reason": "INVALID_CURRENCY",
    }


# ---------------------------------------------------------------------------
# Risk-level mapping
# ---------------------------------------------------------------------------

class TestRiskLevel:
    def test_low_risk_score_0(self):
        assert _get_risk_level(0) == "LOW"

    def test_low_risk_score_2(self):
        assert _get_risk_level(2) == "LOW"

    def test_medium_risk_score_3(self):
        assert _get_risk_level(3) == "MEDIUM"

    def test_medium_risk_score_6(self):
        assert _get_risk_level(6) == "MEDIUM"

    def test_high_risk_score_7(self):
        assert _get_risk_level(7) == "HIGH"

    def test_high_risk_score_10(self):
        assert _get_risk_level(10) == "HIGH"


# ---------------------------------------------------------------------------
# No-trigger scenario (LOW risk)
# ---------------------------------------------------------------------------

class TestLowRisk:
    def test_small_us_daytime_transaction(self, validated_transaction):
        result = process_message(validated_transaction)
        assert result["fraud_risk_score"] == 0
        assert result["fraud_risk_level"] == "LOW"
        assert result["fraud_triggers"] == []

    def test_metadata_added(self, validated_transaction):
        result = process_message(validated_transaction)
        assert "fraud_scored_at" in result
        assert result["source_agent"] == "fraud_detector"
        assert result["target_agent"] == "settlement_processor"


# ---------------------------------------------------------------------------
# Amount triggers
# ---------------------------------------------------------------------------

class TestAmountTriggers:
    def test_amount_above_10k(self, validated_transaction):
        validated_transaction["amount"] = "15000.00"
        result = process_message(validated_transaction)
        assert result["fraud_risk_score"] == 3
        assert result["fraud_risk_level"] == "MEDIUM"
        assert "amount>10k(+3)" in result["fraud_triggers"]

    def test_amount_exactly_10k_no_trigger(self, validated_transaction):
        validated_transaction["amount"] = "10000.00"
        result = process_message(validated_transaction)
        assert result["fraud_risk_score"] == 0
        assert result["fraud_risk_level"] == "LOW"

    def test_amount_above_50k(self, validated_transaction):
        validated_transaction["amount"] = "75000.00"
        result = process_message(validated_transaction)
        # +3 for >10k, +4 for >50k = 7
        assert result["fraud_risk_score"] == 7
        assert result["fraud_risk_level"] == "HIGH"
        assert "amount>10k(+3)" in result["fraud_triggers"]
        assert "amount>50k(+4)" in result["fraud_triggers"]

    def test_amount_exactly_50k_no_extra_trigger(self, validated_transaction):
        validated_transaction["amount"] = "50000.00"
        result = process_message(validated_transaction)
        # Only +3 for >10k, not +4 since exactly 50k, not above
        assert result["fraud_risk_score"] == 3
        assert result["fraud_risk_level"] == "MEDIUM"


# ---------------------------------------------------------------------------
# Unusual-hour trigger
# ---------------------------------------------------------------------------

class TestUnusualHour:
    def test_2am_triggers(self, validated_transaction):
        validated_transaction["timestamp"] = "2026-03-16T02:00:00Z"
        result = process_message(validated_transaction)
        assert result["fraud_risk_score"] == 2
        assert result["fraud_risk_level"] == "LOW"

    def test_3am_triggers(self, validated_transaction):
        validated_transaction["timestamp"] = "2026-03-16T03:30:00Z"
        result = process_message(validated_transaction)
        assert result["fraud_risk_score"] == 2

    def test_4_59am_triggers(self, validated_transaction):
        validated_transaction["timestamp"] = "2026-03-16T04:59:00Z"
        result = process_message(validated_transaction)
        assert result["fraud_risk_score"] == 2

    def test_5am_no_trigger(self, validated_transaction):
        validated_transaction["timestamp"] = "2026-03-16T05:00:00Z"
        result = process_message(validated_transaction)
        assert result["fraud_risk_score"] == 0

    def test_1am_no_trigger(self, validated_transaction):
        validated_transaction["timestamp"] = "2026-03-16T01:59:00Z"
        result = process_message(validated_transaction)
        assert result["fraud_risk_score"] == 0


# ---------------------------------------------------------------------------
# Cross-border trigger
# ---------------------------------------------------------------------------

class TestCrossBorder:
    def test_non_us_country(self, validated_transaction):
        validated_transaction["metadata"]["country"] = "DE"
        result = process_message(validated_transaction)
        assert result["fraud_risk_score"] == 1
        assert "cross_border(DE,+1)" in result["fraud_triggers"]

    def test_us_country_no_trigger(self, validated_transaction):
        result = process_message(validated_transaction)
        assert result["fraud_risk_score"] == 0

    def test_missing_metadata_defaults_us(self, validated_transaction):
        del validated_transaction["metadata"]
        result = process_message(validated_transaction)
        assert result["fraud_risk_score"] == 0


# ---------------------------------------------------------------------------
# Combined triggers
# ---------------------------------------------------------------------------

class TestCombinedTriggers:
    def test_all_triggers_combined(self, validated_transaction):
        validated_transaction["amount"] = "75000.00"
        validated_transaction["timestamp"] = "2026-03-16T03:00:00Z"
        validated_transaction["metadata"]["country"] = "GB"
        result = process_message(validated_transaction)
        # +3 (>10k) +4 (>50k) +2 (unusual hour) +1 (cross-border) = 10
        assert result["fraud_risk_score"] == 10
        assert result["fraud_risk_level"] == "HIGH"

    def test_score_capped_at_10(self, validated_transaction):
        """Even if theoretical sum exceeds 10, score should be capped."""
        validated_transaction["amount"] = "75000.00"
        validated_transaction["timestamp"] = "2026-03-16T03:00:00Z"
        validated_transaction["metadata"]["country"] = "GB"
        result = process_message(validated_transaction)
        assert result["fraud_risk_score"] <= 10


# ---------------------------------------------------------------------------
# Rejected passthrough
# ---------------------------------------------------------------------------

class TestRejectedPassthrough:
    def test_rejected_passes_through(self, rejected_transaction):
        result = process_message(rejected_transaction)
        assert result["status"] == "rejected"
        assert "fraud_risk_score" not in result
        assert result["source_agent"] == "fraud_detector"
        assert result["target_agent"] == "settlement_processor"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_missing_timestamp(self, validated_transaction):
        del validated_transaction["timestamp"]
        result = process_message(validated_transaction)
        # Should not crash, just no unusual hour trigger
        assert "fraud_risk_score" in result

    def test_invalid_timestamp_string(self, validated_transaction):
        validated_transaction["timestamp"] = "not-a-date"
        result = process_message(validated_transaction)
        assert "fraud_risk_score" in result

    def test_invalid_amount_string(self, validated_transaction):
        validated_transaction["amount"] = "invalid"
        result = process_message(validated_transaction)
        # Should treat as 0 and not crash
        assert result["fraud_risk_score"] == 0


class TestMaskAccount:
    def test_masks_account(self):
        assert _mask_account("ACC-1001") == "ACC-***1"

