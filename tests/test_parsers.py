import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.parsers import normalize_timestamp, parse_events


class TestParsers(unittest.TestCase):
    def test_timestamp_converts_to_utc(self):
        result = normalize_timestamp("2026-10-18T12:00:00+05:30")
        self.assertEqual(result, "2026-10-18T06:30:00+00:00")

    def test_naive_timestamp_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "no timezone"):
            normalize_timestamp("2026-10-18T12:00:00")

    def test_invalid_timestamp_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid event timestamp"):
            normalize_timestamp("not-a-timestamp")

    def test_csv_is_parsed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.csv"
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(
                    stream,
                    fieldnames=[
                        "timestamp",
                        "source_type",
                        "action",
                        "source_reference",
                        "account_id",
                        "object_reference",
                    ],
                )
                writer.writeheader()
                writer.writerow({
                    "timestamp": "2026-10-18T12:00:00Z",
                    "source_type": "SYSTEM",
                    "action": "login",
                    "source_reference": "events.csv:2",
                    "account_id": "user-1",
                    "object_reference": "/home/user/file.txt",
                })

            events = parse_events(path)
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["event_id"], "E0001")
            self.assertEqual(events[0]["source_type"], "system")
            self.assertEqual(events[0]["account_id"], "user-1")
            self.assertEqual(events[0]["timestamp"], "2026-10-18T12:00:00+00:00")

    def test_json_is_parsed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.json"
            path.write_text(json.dumps([{
                "timestamp": "2026-10-18T12:00:00Z",
                "source_type": "browser",
                "action": "visit",
                "source_reference": "events.json:1",
            }]), encoding="utf-8")

            events = parse_events(path)
            self.assertEqual(len(events), 1)
            self.assertIsNone(events[0]["account_id"])
            self.assertIsNone(events[0]["object_reference"])

    def test_missing_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                parse_events(Path(directory) / "missing.json")

    def test_unsupported_extension_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.txt"
            path.write_text("test", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Unsupported input format"):
                parse_events(path)


if __name__ == "__main__":
    unittest.main()
