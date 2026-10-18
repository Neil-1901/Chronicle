from datetime import datetime
from typing import Any


def build_timeline(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return events ordered by UTC timestamp without modifying the originals."""
    validated = []

    for event in events:
        if not isinstance(event, dict):
            raise ValueError("Every timeline event must be a dictionary")

        timestamp = event.get("timestamp")
        if not isinstance(timestamp, str) or not timestamp.strip():
            raise ValueError("Every event must have a timestamp")

        text = timestamp.strip()
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"

        try:
            parsed = datetime.fromisoformat(text)
        except ValueError as exc:
            raise ValueError(f"Invalid timestamp: {timestamp!r}") from exc

        if parsed.tzinfo is None:
            raise ValueError(
                f"Timestamp has no timezone: {timestamp!r}"
            )

        validated.append((parsed.timestamp(), event))

    # Stable ordering: events with identical timestamps retain input order.
    validated.sort(key=lambda item: item[0])

    return [event.copy() for _, event in validated]
