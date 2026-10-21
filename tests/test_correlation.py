import unittest

from src.correlation import (
    detect_failed_logins_then_success,
    detect_dns_query_response,
    detect_login_then_file_activity,
    detect_staging_then_transfer,
)


class TestCorrelation(unittest.TestCase):
    def test_dns_rule_requires_matching_transaction_and_reversed_endpoints(self):
        events = [
            {"event_id": "PCAP-E0013", "source_id": "HTTP-CAP-01", "timestamp": "2004-05-13T10:17:09Z", "source_type": "network", "action": "dns_query", "source_reference": "http.cap#frame=13", "attributes": {"dns_transaction_id": "35", "source_ip": "145.254.160.237", "source_port": 3009, "destination_ip": "145.253.2.203", "destination_port": 53}},
            {"event_id": "PCAP-E0017", "source_id": "HTTP-CAP-01", "timestamp": "2004-05-13T10:17:10Z", "source_type": "network", "action": "dns_response", "source_reference": "http.cap#frame=17", "attributes": {"dns_transaction_id": "35", "paired_query_event_id": "PCAP-E0013", "source_ip": "145.253.2.203", "source_port": 53, "destination_ip": "145.254.160.237", "destination_port": 3009}},
        ]
        finding = detect_dns_query_response(events)[0]
        self.assertEqual(finding["rule_id"], "CORR-004")
        self.assertEqual(finding["supporting_event_ids"], ["PCAP-E0013", "PCAP-E0017"])
        self.assertEqual(finding["source_references"], ["http.cap#frame=13", "http.cap#frame=17"])
        altered = [{**events[1], "attributes": {**events[1]["attributes"], "dns_transaction_id": "36"}}]
        self.assertEqual(detect_dns_query_response([events[0], *altered]), [])

    def test_archive_then_upload_links_exact_records_and_states_limit(self):
        events = [
            {"event_id": "GH-E1", "source_id": "ENDPOINT-01", "timestamp": "2026-10-18T10:00:00Z", "account_id": "svc", "source_type": "file_activity", "action": "archive_created", "source_reference": "endpoint:1", "attributes": {"host": "WS-1"}},
            {"event_id": "GH-E2", "source_id": "NETWORK-01", "timestamp": "2026-10-18T10:10:00Z", "account_id": "svc", "source_type": "network", "action": "network_upload", "source_reference": "proxy:2", "attributes": {"host": "WS-1"}},
        ]
        finding = detect_staging_then_transfer(events)[0]
        self.assertEqual(finding["supporting_event_ids"], ["GH-E1", "GH-E2"])
        self.assertEqual(finding["supporting_records"][1]["source_reference"], "proxy:2")
        self.assertTrue(finding["alternative_explanations"])

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
