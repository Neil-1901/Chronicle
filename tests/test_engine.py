import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.engine import run_investigation


class TestEngine(unittest.TestCase):
    def test_full_investigation_pipeline(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / "evidence"
            evidence.mkdir()

            events_file = evidence / "events.json"
            events = [
                {
                    "timestamp": "2026-10-18T10:00:00Z",
                    "source_type": "authentication",
                    "account_id": "demo-user",
                    "action": "login_failure",
                    "source_reference": "events.json:1",
                },
                {
                    "timestamp": "2026-10-18T10:02:00Z",
                    "source_type": "authentication",
                    "account_id": "demo-user",
                    "action": "login_failure",
                    "source_reference": "events.json:2",
                },
                {
                    "timestamp": "2026-10-18T10:03:00Z",
                    "source_type": "authentication",
                    "account_id": "demo-user",
                    "action": "login_failure",
                    "source_reference": "events.json:3",
                },
                {
                    "timestamp": "2026-10-18T10:04:00Z",
                    "source_type": "authentication",
                    "account_id": "demo-user",
                    "action": "login_success",
                    "source_reference": "events.json:4",
                },
            ]
            events_file.write_text(json.dumps(events), encoding="utf-8")

            output = root / "outputs" / "report.json"
            report = run_investigation(
                case_id="CASE-TEST-001",
                evidence_dir=evidence,
                events_file=events_file,
                output_report=output,
            )

            self.assertTrue(output.is_file())
            self.assertEqual(report["case_id"], "CASE-TEST-001")
            self.assertEqual(len(report["timeline"]), 4)
            self.assertEqual(len(report["findings"]), 1)
            self.assertEqual(
                report["findings"][0]["rule_id"],
                "CORR-001",
            )

            manifest = report["evidence_summary"]["files"]
            self.assertEqual(len(manifest), 1)
            self.assertEqual(manifest[0]["relative_path"], "events.json")
            self.assertTrue(manifest[0]["sha256"])

            saved = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(saved["case_id"], "CASE-TEST-001")

    def test_missing_evidence_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            with self.assertRaises(FileNotFoundError):
                run_investigation(
                    case_id="CASE-TEST-002",
                    evidence_dir=root / "missing",
                    events_file=root / "events.json",
                    output_report=root / "report.json",
                )


if __name__ == "__main__":
    unittest.main()
