import unittest

from fastapi import HTTPException

from src.api import get_cases, investigate_case


class TestCaseApi(unittest.TestCase):
    def test_lists_three_cases_as_separate_tracks(self):
        response = get_cases()
        ids = {item["case_id"] for item in response["cases"]}
        self.assertEqual(ids, {"CHRONICLE-DEMO-001", "OPERATION-GLASSHOUSE", "WIRESHARK-PRACTICE-001"})

    def test_unknown_case_returns_404(self):
        with self.assertRaises(HTTPException) as raised:
            investigate_case("NOT-A-CASE")
        self.assertEqual(raised.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
