import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from src.manifest import create_manifest


class TestManifest(unittest.TestCase):
    def test_manifest_records_hash_and_size(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "evidence"
            root.mkdir()
            evidence = root / "sample.txt"
            content = b"simulated forensic evidence"
            evidence.write_bytes(content)
            output = Path(directory) / "manifest.csv"

            count = create_manifest(root, output)

            with output.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))

            self.assertEqual(count, 1)
            self.assertEqual(rows[0]["relative_path"], "sample.txt")
            self.assertEqual(int(rows[0]["size_bytes"]), len(content))
            self.assertEqual(rows[0]["sha256"], hashlib.sha256(content).hexdigest())
            self.assertTrue(rows[0]["collected_at_utc"].endswith("+00:00"))

    def test_empty_directory_produces_header_only_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "evidence"
            root.mkdir()
            output = Path(directory) / "manifest.csv"

            count = create_manifest(root, output)

            with output.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))

            self.assertEqual(count, 0)
            self.assertEqual(rows, [])

    def test_nested_files_are_included(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "evidence"
            nested = root / "browser"
            nested.mkdir(parents=True)
            (nested / "events.json").write_text("{}", encoding="utf-8")
            output = Path(directory) / "manifest.csv"

            count = create_manifest(root, output)

            with output.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))

            self.assertEqual(count, 1)
            self.assertEqual(rows[0]["relative_path"], "browser/events.json")

    def test_missing_evidence_directory_raises_error(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing"
            output = Path(directory) / "manifest.csv"

            with self.assertRaises(FileNotFoundError):
                create_manifest(missing, output)


if __name__ == "__main__":
    unittest.main()
