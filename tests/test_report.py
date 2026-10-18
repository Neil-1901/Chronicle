import json
import tempfile
import unittest
from pathlib import Path

from src.report import generate_report


class TestReport(unittest.TestCase):
    def test_report_contains_all_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "report.json"

            report = generate_report(
                case_id="CASE-001",
                evidence_manifest=[
                    {"relative_path": "events.json", "sha256": "abc123"}
                ],
                timeline=[{"event_id": "E0001", "action": "login_success"}],
                findings=[{"rule_id": "CORR-001", "supporting_event_ids": ["E0001"]}],
                output_path=output,
            )

            self.assertEqual(report["case_id"], "CASE-001")
            self.assertEqual(report["evidence_summary"]["file_count"], 1)
            self.assertEqual(len(report["timeline"]), 1)
            self.assertEqual(len(report["findings"]), 1)
            self.assertTrue(report["limitations"])
            self.assertTrue(output.is_file())

    def test_saved_json_matches_returned_report(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "report.json"

            report = generate_report(
                "CASE-002", [], [], [], output
            )

            saved = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(saved, report)

    def test_empty_case_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "case_id"):
                generate_report("", [], [], [], Path(directory) / "report.json")

    def test_non_list_sections_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "timeline must be a list"):
                generate_report(
                    "CASE-003",
                    [],
                    {},
                    [],
                    Path(directory) / "report.json",
                )


if __name__ == "__main__":
    unittest.main()

