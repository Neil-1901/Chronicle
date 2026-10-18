import hashlib
import tempfile
import unittest
from pathlib import Path

from src.hashing import calculate_sha256, verify_sha256


class TestHashing(unittest.TestCase):
    def test_hash_matches_known_value(self):
        with tempfile.TemporaryDirectory() as directory:
            evidence = Path(directory) / "evidence.txt"
            evidence.write_bytes(b"Chronicle forensic evidence")
            expected = hashlib.sha256(b"Chronicle forensic evidence").hexdigest()
            self.assertEqual(calculate_sha256(evidence), expected)

    def test_same_file_has_same_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            evidence = Path(directory) / "evidence.txt"
            evidence.write_bytes(b"unchanged evidence")
            self.assertEqual(calculate_sha256(evidence), calculate_sha256(evidence))

    def test_modified_file_fails_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            evidence = Path(directory) / "evidence.txt"
            evidence.write_bytes(b"original evidence")
            original_hash = calculate_sha256(evidence)
            evidence.write_bytes(b"modified evidence")
            self.assertFalse(verify_sha256(evidence, original_hash))

    def test_matching_hash_passes_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            evidence = Path(directory) / "evidence.txt"
            evidence.write_bytes(b"valid evidence")
            self.assertTrue(verify_sha256(evidence, calculate_sha256(evidence)))

    def test_empty_file_can_be_hashed(self):
        with tempfile.TemporaryDirectory() as directory:
            evidence = Path(directory) / "empty.txt"
            evidence.write_bytes(b"")
            self.assertEqual(calculate_sha256(evidence), hashlib.sha256(b"").hexdigest())


if __name__ == "__main__":
    unittest.main()
