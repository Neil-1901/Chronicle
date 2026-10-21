import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.cases import CASES
from src.engine import run_investigation

ROOT = Path(__file__).resolve().parents[1]


class TestNetworkPracticeCase(unittest.TestCase):
    def setUp(self):
        self.case = CASES["WIRESHARK-PRACTICE-001"]
        self.export = json.loads(self.case["events_file"].read_text(encoding="utf-8"))

    def test_export_has_stable_frame_ids_and_traceable_exhibit_annotations(self):
        events = self.export["events"]
        self.assertEqual(len(events), 43)
        self.assertEqual([event["event_id"] for event in events], [f"PCAP-E{i:04d}" for i in range(1, 44)])
        self.assertEqual([event["attributes"]["frame_number"] for event in events], list(range(1, 44)))
        self.assertEqual(self.export["source_capture"]["sha256"], hashlib.sha256(self.case["additional_files"][0]["path"].read_bytes()).hexdigest())
        http = {event["attributes"]["frame_number"]: event for event in events if event["action"].startswith("http_")}
        self.assertEqual(set(http), {4, 18, 27, 38})
        self.assertEqual(http[4]["attributes"]["host"], "www.ethereal.com")
        self.assertIn("Windows NT 5.1", http[4]["attributes"]["user_agent"])
        self.assertEqual(http[27]["action"], "http_response")
        self.assertEqual(http[38]["action"], "http_response")
        dns = [event for event in events if event["action"].startswith("dns_")]
        self.assertEqual([event["attributes"]["frame_number"] for event in dns], [13, 17])
        self.assertEqual(dns[1]["attributes"]["paired_query_event_id"], dns[0]["event_id"])
        self.assertIn("pagead2.google.com.", dns[1]["attributes"]["decoded_summary"])

    def test_investigation_validates_capture_lineage_and_dns_finding(self):
        with tempfile.TemporaryDirectory() as directory:
            report = run_investigation(
                self.case["case_id"], self.case["evidence_dir"], self.case["events_file"],
                Path(directory) / "report.json", self.case,
            )
        self.assertEqual(report["case_kind"], "public-sample")
        self.assertEqual(report["event_count"], 43)
        provenance = next(stage for stage in report["pipeline"] if stage["stage_id"] == "packet_provenance")
        self.assertTrue(all(provenance["output"]["checks"].values()))
        finding = next(finding for finding in report["findings"] if finding["rule_id"] == "CORR-004")
        self.assertEqual(finding["supporting_event_ids"], ["PCAP-E0013", "PCAP-E0017"])
        refs = {event["event_id"]: event["source_reference"] for event in report["timeline"]}
        self.assertEqual([refs[event_id] for event_id in finding["supporting_event_ids"]], finding["source_references"])
        self.assertIn("not incident evidence", report["examination"]["limitations"][0])
        self.assertEqual(report["evidence_summary"]["file_count"], 5)

    def test_modified_export_capture_digest_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "evidence"
            root.mkdir()
            altered = json.loads(json.dumps(self.export))
            altered["events"][0]["attributes"]["capture_sha256"] = "0" * 64
            event_file = root / "observations.json"
            event_file.write_text(json.dumps(altered), encoding="utf-8")
            case = {**self.case, "evidence_dir": root, "events_file": event_file}
            with self.assertRaisesRegex(ValueError, "capture_digest_matches|observations_reference_capture_digest"):
                run_investigation(case["case_id"], root, event_file, Path(directory) / "report.json", case)


if __name__ == "__main__":
    unittest.main()
