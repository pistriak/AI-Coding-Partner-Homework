"""Integration tests — full pipeline end-to-end using tmp_path isolation."""

import json
import shutil
import pytest
from pathlib import Path

from agents.transaction_validator import process_message as validate
from agents.fraud_detector import process_message as detect_fraud
from agents.settlement_processor import process_message as settle


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_TRANSACTIONS_PATH = Path(__file__).resolve().parent.parent / "sample-transactions.json"


@pytest.fixture
def sample_transactions():
    with open(SAMPLE_TRANSACTIONS_PATH, "r") as f:
        return json.load(f)


@pytest.fixture
def results_dir(tmp_path):
    d = tmp_path / "results"
    d.mkdir()
    return d


# ---------------------------------------------------------------------------
# Full pipeline tests
# ---------------------------------------------------------------------------

class TestFullPipeline:
    def _run_pipeline(self, transactions):
        """Run 3-agent pipeline on a list of transactions, return results."""
        results = []
        for txn in transactions:
            validated = validate(txn)
            scored = detect_fraud(validated)
            settled = settle(scored)
            results.append(settled)
        return results

    def test_processes_all_8_transactions(self, sample_transactions):
        results = self._run_pipeline(sample_transactions)
        assert len(results) == 8

    def test_all_results_have_status(self, sample_transactions):
        results = self._run_pipeline(sample_transactions)
        for r in results:
            assert "status" in r
            assert r["status"] in ("settled", "flagged_for_review", "rejected")

    def test_txn001_settled_low_risk(self, sample_transactions):
        results = self._run_pipeline(sample_transactions)
        txn001 = next(r for r in results if r["transaction_id"] == "TXN001")
        assert txn001["status"] == "settled"
        assert txn001["fraud_risk_level"] == "LOW"
        assert txn001["fraud_risk_score"] == 0

    def test_txn002_settled_medium_risk(self, sample_transactions):
        results = self._run_pipeline(sample_transactions)
        txn002 = next(r for r in results if r["transaction_id"] == "TXN002")
        assert txn002["status"] == "settled"
        assert txn002["fraud_risk_level"] == "MEDIUM"
        assert txn002["fraud_risk_score"] == 3

    def test_txn004_medium_risk_unusual_hour_cross_border(self, sample_transactions):
        results = self._run_pipeline(sample_transactions)
        txn004 = next(r for r in results if r["transaction_id"] == "TXN004")
        assert txn004["status"] == "settled"
        assert txn004["fraud_risk_level"] == "MEDIUM"
        assert txn004["fraud_risk_score"] == 3  # +2 unusual hour + 1 cross-border

    def test_txn005_flagged_high_risk(self, sample_transactions):
        results = self._run_pipeline(sample_transactions)
        txn005 = next(r for r in results if r["transaction_id"] == "TXN005")
        assert txn005["status"] == "flagged_for_review"
        assert txn005["fraud_risk_level"] == "HIGH"
        assert txn005["fraud_risk_score"] == 7

    def test_txn006_rejected_invalid_currency(self, sample_transactions):
        results = self._run_pipeline(sample_transactions)
        txn006 = next(r for r in results if r["transaction_id"] == "TXN006")
        assert txn006["status"] == "rejected"
        assert txn006["rejection_reason"] == "INVALID_CURRENCY"

    def test_txn007_rejected_negative_amount(self, sample_transactions):
        results = self._run_pipeline(sample_transactions)
        txn007 = next(r for r in results if r["transaction_id"] == "TXN007")
        assert txn007["status"] == "rejected"
        assert txn007["rejection_reason"] == "INVALID_AMOUNT"

    def test_txn008_settled_low_risk(self, sample_transactions):
        results = self._run_pipeline(sample_transactions)
        txn008 = next(r for r in results if r["transaction_id"] == "TXN008")
        assert txn008["status"] == "settled"
        assert txn008["fraud_risk_level"] == "LOW"

    def test_result_counts(self, sample_transactions):
        results = self._run_pipeline(sample_transactions)
        settled = sum(1 for r in results if r["status"] == "settled")
        flagged = sum(1 for r in results if r["status"] == "flagged_for_review")
        rejected = sum(1 for r in results if r["status"] == "rejected")
        assert settled == 5
        assert flagged == 1
        assert rejected == 2


# ---------------------------------------------------------------------------
# File-based output tests
# ---------------------------------------------------------------------------

class TestFileOutput:
    def test_results_written_to_disk(self, sample_transactions, results_dir):
        for txn in sample_transactions:
            validated = validate(txn)
            scored = detect_fraud(validated)
            settled = settle(scored)
            filepath = results_dir / f"{txn['transaction_id']}.json"
            with open(filepath, "w") as f:
                json.dump(settled, f, indent=2, default=str)

        files = list(results_dir.glob("*.json"))
        assert len(files) == 8

    def test_result_files_are_valid_json(self, sample_transactions, results_dir):
        for txn in sample_transactions:
            validated = validate(txn)
            scored = detect_fraud(validated)
            settled = settle(scored)
            filepath = results_dir / f"{txn['transaction_id']}.json"
            with open(filepath, "w") as f:
                json.dump(settled, f, indent=2, default=str)

        for fp in results_dir.glob("*.json"):
            with open(fp) as f:
                data = json.load(f)
                assert "transaction_id" in data
                assert "status" in data


# ---------------------------------------------------------------------------
# Integrator module tests
# ---------------------------------------------------------------------------

class TestIntegratorModule:
    def test_run_pipeline_returns_results(self, tmp_path, monkeypatch):
        """Test the integrator.run_pipeline function with isolated dirs."""
        import integrator

        monkeypatch.setattr(integrator, "SHARED_DIR", tmp_path / "shared")
        monkeypatch.setattr(integrator, "INPUT_DIR", tmp_path / "shared" / "input")
        monkeypatch.setattr(integrator, "PROCESSING_DIR", tmp_path / "shared" / "processing")
        monkeypatch.setattr(integrator, "OUTPUT_DIR", tmp_path / "shared" / "output")
        monkeypatch.setattr(integrator, "RESULTS_DIR", tmp_path / "shared" / "results")

        integrator._setup_directories()
        results = integrator.run_pipeline()
        assert len(results) == 8

    def test_print_summary_does_not_crash(self, tmp_path, monkeypatch, capsys):
        """Test print_summary works without errors."""
        import integrator

        monkeypatch.setattr(integrator, "SHARED_DIR", tmp_path / "shared")
        monkeypatch.setattr(integrator, "INPUT_DIR", tmp_path / "shared" / "input")
        monkeypatch.setattr(integrator, "PROCESSING_DIR", tmp_path / "shared" / "processing")
        monkeypatch.setattr(integrator, "OUTPUT_DIR", tmp_path / "shared" / "output")
        monkeypatch.setattr(integrator, "RESULTS_DIR", tmp_path / "shared" / "results")

        integrator._setup_directories()
        results = integrator.run_pipeline()
        integrator.print_summary(results)

        captured = capsys.readouterr()
        assert "Pipeline Results Summary" in captured.out
        assert "Total: 8" in captured.out

