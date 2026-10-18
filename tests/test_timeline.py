import unittest

from src.timeline import build_timeline


class TestTimeline(unittest.TestCase):
    def test_events_are_sorted_chronologically(self):
        events = [
            {"event_id": "E0002", "timestamp": "2026-10-18T12:00:00Z"},
            {"event_id": "E0001", "timestamp": "2026-10-18T10:00:00Z"},
        ]

        result = build_timeline(events)

        self.assertEqual(
            [event["event_id"] for event in result],
            ["E0001", "E0002"],
        )

    def test_same_timestamp_preserves_input_order(self):
        events = [
            {"event_id": "E0002", "timestamp": "2026-10-18T10:00:00Z"},
            {"event_id": "E0001", "timestamp": "2026-10-18T10:00:00Z"},
        ]

        result = build_timeline(events)

        self.assertEqual(
            [event["event_id"] for event in result],
            ["E0002", "E0001"],
        )

    def test_timezone_offsets_are_compared_correctly(self):
        events = [
            {"event_id": "later", "timestamp": "2026-10-18T10:00:00Z"},
            {"event_id": "earlier", "timestamp": "2026-10-18T12:00:00+05:30"},
        ]

        result = build_timeline(events)

        self.assertEqual(
            [event["event_id"] for event in result],
            ["earlier", "later"],
        )

    def test_missing_timestamp_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must have a timestamp"):
            build_timeline([{"event_id": "E0001"}])

    def test_timezone_naive_timestamp_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "no timezone"):
            build_timeline([
                {"event_id": "E0001", "timestamp": "2026-10-18T10:00:00"}
            ])

    def test_input_list_is_not_reordered(self):
        events = [
            {"event_id": "E0002", "timestamp": "2026-10-18T12:00:00Z"},
            {"event_id": "E0001", "timestamp": "2026-10-18T10:00:00Z"},
        ]

        build_timeline(events)

        self.assertEqual(events[0]["event_id"], "E0002")


if __name__ == "__main__":
    unittest.main()
