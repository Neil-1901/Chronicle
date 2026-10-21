import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.cases import CASES
from src.engine import run_investigation

ROOT = Path(__file__).resolve().parents[1]


class TestGlasshouse(unittest.TestCase):
    def test_dataset_has_240_stable_chronological_events(self):
        path = ROOT / "data/cases/operation-glasshouse/events.csv"
        with path.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 240)
        ids = [row["event_id"] for row in rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids[0], "GH-E0001")
        self.assertEqual(ids[-1], "GH-E0240")
        self.assertEqual([r["timestamp"] for r in rows], sorted(r["timestamp"] for r in rows))
        self.assertEqual({r["source_type"] for r in rows}, {"authentication", "file_activity", "network"})

    def test_report_findings_trace_to_event_records(self):
        case = CASES["OPERATION-GLASSHOUSE"]
        with tempfile.TemporaryDirectory() as directory:
            report = run_investigation(case["case_id"], case["evidence_dir"], case["events_file"], Path(directory) / "report.json", case)
        events = {event["event_id"]: event for event in report["timeline"]}
        self.assertEqual(report["event_count"], 240)
        self.assertEqual(report["case_id"], "OPERATION-GLASSHOUSE")
        self.assertIn("CHRONICLE-DEMO-001", CASES)
        self.assertNotEqual(CASES["CHRONICLE-DEMO-001"]["case_id"], case["case_id"])
        self.assertTrue(report["pipeline"])
        self.assertEqual(report["event_type_counts"]["network"], 78)
        self.assertEqual(sum(report["evidence_summary"]["source_record_counts"].values()), 240)
        for finding in report["findings"]:
            for event_id in finding["supporting_event_ids"]:
                self.assertIn(event_id, events)
            for record in finding["supporting_records"]:
                self.assertIn(record["event_id"], events)
                self.assertEqual(record["timestamp"], events[record["event_id"]]["timestamp"])
        truth = json.loads((ROOT / "data/evaluation/operation-glasshouse-ground-truth.json").read_text(encoding="utf-8"))
        rule_pairs = {frozenset(finding["supporting_event_ids"]) for finding in report["findings"] if finding["rule_id"] == "CORR-003"}
        expected_suspicious_pair = frozenset(
            event_id for event_id in truth["known_sequence_event_ids"]
            if events[event_id]["action"] in {"archive_created", "network_upload"}
        )
        self.assertIn(expected_suspicious_pair, rule_pairs)
        self.assertIn(frozenset(truth["benign_sequence_event_ids"]), rule_pairs)

    def test_ground_truth_is_separate_and_original_demo_has_six_rows(self):
        path = ROOT / "data/evaluation/operation-glasshouse-ground-truth.json"
        truth = json.loads(path.read_text(encoding="utf-8"))
        self.assertIn("never a Chronicle finding", truth["label"])
        case = CASES["CHRONICLE-DEMO-001"]
        with case["events_file"].open(newline="", encoding="utf-8") as stream:
            self.assertEqual(len(list(csv.DictReader(stream))), 6)
        with tempfile.TemporaryDirectory() as directory:
            report = run_investigation(case["case_id"], case["evidence_dir"], case["events_file"], Path(directory) / "demo.json", case)
        self.assertEqual(len(report["timeline"]), 6)
        self.assertEqual({finding["rule_id"] for finding in report["findings"]}, {"CORR-001", "CORR-002"})


if __name__ == "__main__":
    unittest.main()
