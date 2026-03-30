"""Tests for the Transaction Validator agent."""

import decimal
import pytest
from agents.transaction_validator import process_message, _mask_account, VALID_CURRENCIES


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_transaction():
    """Return a minimal valid transaction dict."""
    return {
        "transaction_id": "TXN-TEST-001",
        "amount": "1500.00",
        "currency": "USD",
        "source_account": "ACC-1001",
        "destination_account": "ACC-2001",
        "timestamp": "2026-03-16T09:00:00Z",
        "transaction_type": "transfer",
        "metadata": {"channel": "online", "country": "US"},
    }


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

class TestValidTransaction:
    def test_valid_transaction_returns_validated(self, valid_transaction):
        result = process_message(valid_transaction)
        assert result["status"] == "validated"

    def test_valid_transaction_preserves_fields(self, valid_transaction):
        result = process_message(valid_transaction)
        assert result["transaction_id"] == "TXN-TEST-001"
        assert result["amount"] == "1500.00"
        assert result["currency"] == "USD"

    def test_valid_transaction_adds_metadata(self, valid_transaction):
        result = process_message(valid_transaction)
        assert "validated_at" in result
        assert result["source_agent"] == "transaction_validator"
        assert result["target_agent"] == "fraud_detector"

    def test_all_valid_currencies(self, valid_transaction):
        for currency in VALID_CURRENCIES:
            valid_transaction["currency"] = currency
            result = process_message(valid_transaction)
            assert result["status"] == "validated", f"Failed for currency {currency}"

    def test_decimal_amount_string(self, valid_transaction):
        valid_transaction["amount"] = "0.01"
        result = process_message(valid_transaction)
        assert result["status"] == "validated"

    def test_large_amount(self, valid_transaction):
        valid_transaction["amount"] = "99999999.99"
        result = process_message(valid_transaction)
        assert result["status"] == "validated"


# ---------------------------------------------------------------------------
# Missing-field tests
# ---------------------------------------------------------------------------

class TestMissingFields:
    @pytest.mark.parametrize("field", [
        "transaction_id",
        "amount",
        "currency",
        "source_account",
        "destination_account",
    ])
    def test_missing_required_field_rejected(self, valid_transaction, field):
        del valid_transaction[field]
        result = process_message(valid_transaction)
        assert result["status"] == "rejected"
        assert f"MISSING_FIELD:{field}" in result["rejection_reason"]

    def test_empty_string_field_rejected(self, valid_transaction):
        valid_transaction["amount"] = ""
        result = process_message(valid_transaction)
        assert result["status"] == "rejected"

    def test_none_field_rejected(self, valid_transaction):
        valid_transaction["currency"] = None
        result = process_message(valid_transaction)
        assert result["status"] == "rejected"

    def test_whitespace_only_field_rejected(self, valid_transaction):
        valid_transaction["source_account"] = "   "
        result = process_message(valid_transaction)
        assert result["status"] == "rejected"
        assert "MISSING_FIELD" in result["rejection_reason"]


# ---------------------------------------------------------------------------
# Amount-validation tests
# ---------------------------------------------------------------------------

class TestAmountValidation:
    def test_negative_amount_rejected(self, valid_transaction):
        valid_transaction["amount"] = "-100.00"
        result = process_message(valid_transaction)
        assert result["status"] == "rejected"
        assert result["rejection_reason"] == "INVALID_AMOUNT"

    def test_zero_amount_rejected(self, valid_transaction):
        valid_transaction["amount"] = "0"
        result = process_message(valid_transaction)
        assert result["status"] == "rejected"
        assert result["rejection_reason"] == "INVALID_AMOUNT"

    def test_non_numeric_amount_rejected(self, valid_transaction):
        valid_transaction["amount"] = "abc"
        result = process_message(valid_transaction)
        assert result["status"] == "rejected"
        assert result["rejection_reason"] == "INVALID_AMOUNT"

    def test_amount_zero_point_zero_rejected(self, valid_transaction):
        valid_transaction["amount"] = "0.00"
        result = process_message(valid_transaction)
        assert result["status"] == "rejected"
        assert result["rejection_reason"] == "INVALID_AMOUNT"


# ---------------------------------------------------------------------------
# Currency-validation tests
# ---------------------------------------------------------------------------

class TestCurrencyValidation:
    def test_invalid_currency_rejected(self, valid_transaction):
        valid_transaction["currency"] = "XYZ"
        result = process_message(valid_transaction)
        assert result["status"] == "rejected"
        assert result["rejection_reason"] == "INVALID_CURRENCY"

    def test_lowercase_currency_accepted(self, valid_transaction):
        """Currency comparison should be case-insensitive."""
        valid_transaction["currency"] = "usd"
        result = process_message(valid_transaction)
        assert result["status"] == "validated"

    def test_empty_currency_rejected(self, valid_transaction):
        valid_transaction["currency"] = ""
        result = process_message(valid_transaction)
        assert result["status"] == "rejected"


# ---------------------------------------------------------------------------
# Helper tests
# ---------------------------------------------------------------------------

class TestMaskAccount:
    def test_masks_account_number(self):
        assert _mask_account("ACC-1001") == "ACC-***1"

    def test_masks_short_account(self):
        result = _mask_account("A")
        assert result == "***"

    def test_masks_no_dash(self):
        result = _mask_account("ABCDE")
        # rfind("-") returns -1, so prefix is empty string from [:-1+1] = [:0] = ""
        assert "***" in result

