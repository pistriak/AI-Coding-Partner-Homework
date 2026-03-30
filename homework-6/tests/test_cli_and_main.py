"""Tests for transaction_validator CLI/dry-run and integrator main()."""

import json
import pytest
from pathlib import Path

from agents.transaction_validator import dry_run


SAMPLE_TRANSACTIONS_PATH = Path(__file__).resolve().parent.parent / "sample-transactions.json"


class TestDryRun:
    def test_dry_run_prints_summary(self, capsys):
        dry_run(str(SAMPLE_TRANSACTIONS_PATH))
        captured = capsys.readouterr()
        assert "Transaction Validation Summary" in captured.out
        assert "Valid: 6" in captured.out
        assert "Invalid: 2" in captured.out

    def test_dry_run_shows_all_ids(self, capsys):
        dry_run(str(SAMPLE_TRANSACTIONS_PATH))
        captured = capsys.readouterr()
        for i in range(1, 9):
            assert f"TXN00{i}" in captured.out

    def test_dry_run_with_custom_file(self, tmp_path, capsys):
        txns = [
            {
                "transaction_id": "TEST001",
                "amount": "100.00",
                "currency": "USD",
                "source_account": "ACC-1",
                "destination_account": "ACC-2",
            }
        ]
        fp = tmp_path / "test.json"
        with open(fp, "w") as f:
            json.dump(txns, f)

        dry_run(str(fp))
        captured = capsys.readouterr()
        assert "Valid: 1" in captured.out
        assert "Invalid: 0" in captured.out

    def test_dry_run_with_invalid_transaction(self, tmp_path, capsys):
        txns = [
            {
                "transaction_id": "BAD001",
                "amount": "-50",
                "currency": "USD",
                "source_account": "ACC-1",
                "destination_account": "ACC-2",
            }
        ]
        fp = tmp_path / "bad.json"
        with open(fp, "w") as f:
            json.dump(txns, f)

        dry_run(str(fp))
        captured = capsys.readouterr()
        assert "Valid: 0" in captured.out
        assert "Invalid: 1" in captured.out


class TestIntegratorMain:
    def test_main_runs_without_error(self, tmp_path, monkeypatch):
        import integrator

        monkeypatch.setattr(integrator, "SHARED_DIR", tmp_path / "shared")
        monkeypatch.setattr(integrator, "INPUT_DIR", tmp_path / "shared" / "input")
        monkeypatch.setattr(integrator, "PROCESSING_DIR", tmp_path / "shared" / "processing")
        monkeypatch.setattr(integrator, "OUTPUT_DIR", tmp_path / "shared" / "output")
        monkeypatch.setattr(integrator, "RESULTS_DIR", tmp_path / "shared" / "results")
        monkeypatch.setattr(integrator, "LOG_FILE", tmp_path / "test.log")

        integrator.main()

        # Verify results exist
        results = list((tmp_path / "shared" / "results").glob("*.json"))
        assert len(results) == 8

    def test_setup_directories_creates_dirs(self, tmp_path, monkeypatch):
        import integrator

        monkeypatch.setattr(integrator, "INPUT_DIR", tmp_path / "shared" / "input")
        monkeypatch.setattr(integrator, "PROCESSING_DIR", tmp_path / "shared" / "processing")
        monkeypatch.setattr(integrator, "OUTPUT_DIR", tmp_path / "shared" / "output")
        monkeypatch.setattr(integrator, "RESULTS_DIR", tmp_path / "shared" / "results")

        integrator._setup_directories()

        assert (tmp_path / "shared" / "input").exists()
        assert (tmp_path / "shared" / "processing").exists()
        assert (tmp_path / "shared" / "output").exists()
        assert (tmp_path / "shared" / "results").exists()

    def test_write_json(self, tmp_path):
        import integrator

        data = {"key": "value", "num": 42}
        path = integrator._write_json(tmp_path, "test.json", data)

        assert path.exists()
        with open(path) as f:
            loaded = json.load(f)
        assert loaded == data

    def test_wrap_message(self):
        import integrator

        data = {"transaction_id": "TXN-WRAP"}
        msg = integrator._wrap_message(data, "agent_a", "agent_b", "test_type")

        assert msg["source_agent"] == "agent_a"
        assert msg["target_agent"] == "agent_b"
        assert msg["message_type"] == "test_type"
        assert msg["data"] == data
        assert "message_id" in msg
        assert "timestamp" in msg

