import unittest

from src.correlation import (
    detect_failed_logins_then_success,
    detect_login_then_file_activity,
)


class TestCorrelation(unittest.TestCase):
    def setUp(self):
        self.events = [
            {
                "event_id": "E0001",
                "timestamp": "2026-10-18T10:00:00Z",
                "account_id": "user-1",
                "action": "login_failure",
            },
            {
                "event_id": "E0002",
                "timestamp": "2026-10-18T10:02:00Z",
                "account_id": "user-1",
                "action": "login_failure",
            },
            {
                "event_id": "E0003",
                "timestamp": "2026-10-18T10:03:00Z",
                "account_id": "user-1",
                "action": "login_failure",
            },
            {
                "event_id": "E0004",
                "timestamp": "2026-10-18T10:04:00Z",
                "account_id": "user-1",
                "action": "login_success",
            },
        ]

    def test_detects_failures_followed_by_success(self):
        findings = detect_failed_logins_then_success(self.events)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["rule_id"], "CORR-001")
        self.assertEqual(findings[0]["failure_count"], 3)
        self.assertEqual(
            findings[0]["supporting_event_ids"],
            ["E0001", "E0002", "E0003", "E0004"],
        )

    def test_ignores_success_without_enough_failures(self):
        findings = detect_failed_logins_then_success(
            self.events[-2:], threshold=3
        )
        self.assertEqual(findings, [])

    def test_does_not_mix_different_accounts(self):
        events = [
            {**event, "account_id": "another-user"}
            if event["action"] == "login_failure"
            else event
            for event in self.events
        ]
        self.assertEqual(detect_failed_logins_then_success(events), [])

    def test_ignores_failures_outside_window(self):
        events = [
            {
                **self.events[0],
                "timestamp": "2026-10-18T09:00:00Z",
            },
            *self.events[1:],
        ]
        self.assertEqual(
            detect_failed_logins_then_success(events, window_minutes=10),
            [],
        )

    def test_rejects_timezone_naive_timestamp(self):
        events = [{**self.events[0], "timestamp": "2026-10-18T10:00:00"}]
        with self.assertRaisesRegex(ValueError, "no timezone"):
            detect_failed_logins_then_success(events)

    def test_rejects_invalid_threshold(self):
        with self.assertRaisesRegex(ValueError, "threshold"):
            detect_failed_logins_then_success(self.events, threshold=0)



    def test_detects_login_followed_by_file_activity(self):
        events = [
            {
                "event_id": "E0004",
                "timestamp": "2026-10-18T10:04:00Z",
                "account_id": "user-1",
                "action": "login_success",
                "source_type": "authentication",
                "source_reference": "auth.log:4",
            },
            {
                "event_id": "E0005",
                "timestamp": "2026-10-18T10:06:00Z",
                "account_id": "user-1",
                "action": "file_opened",
                "source_type": "file_activity",
                "source_reference": "files.log:5",
            },
        ]

        findings = detect_login_then_file_activity(events)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["rule_id"], "CORR-002")
        self.assertEqual(
            findings[0]["supporting_event_ids"],
            ["E0004", "E0005"],
        )
        self.assertEqual(
            findings[0]["source_references"],
            ["auth.log:4", "files.log:5"],
        )
        self.assertIn("limitation", findings[0])

    def test_ignores_file_activity_for_different_account(self):
        events = [
            {
                "event_id": "E0004",
                "timestamp": "2026-10-18T10:04:00Z",
                "account_id": "user-1",
                "action": "login_success",
            },
            {
                "event_id": "E0005",
                "timestamp": "2026-10-18T10:06:00Z",
                "account_id": "user-2",
                "action": "file_opened",
                "source_type": "file_activity",
            },
        ]

        self.assertEqual(detect_login_then_file_activity(events), [])

    def test_ignores_file_activity_outside_window(self):
        events = [
            {
                "event_id": "E0004",
                "timestamp": "2026-10-18T10:04:00Z",
                "account_id": "user-1",
                "action": "login_success",
            },
            {
                "event_id": "E0005",
                "timestamp": "2026-10-18T10:20:00Z",
                "account_id": "user-1",
                "action": "file_opened",
                "source_type": "file_activity",
            },
        ]

        self.assertEqual(
            detect_login_then_file_activity(events, window_minutes=10),
            [],
        )

    def test_rejects_invalid_file_activity_window(self):
        events = [
            {
                "event_id": "E0004",
                "timestamp": "2026-10-18T10:04:00Z",
                "account_id": "user-1",
                "action": "login_success",
            }
        ]

        with self.assertRaises(ValueError):
            detect_login_then_file_activity(events, window_minutes=0)

if __name__ == "__main__":
    unittest.main()
