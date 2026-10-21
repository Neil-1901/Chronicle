import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = (
    "timestamp",
    "source_type",
    "action",
    "source_reference",
)


def normalize_timestamp(value: str) -> str:
    """Convert a timezone-aware ISO-8601 timestamp to UTC."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Event timestamp is missing")

    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"Invalid event timestamp: {value!r}") from exc

    if parsed.tzinfo is None:
        raise ValueError(
            f"Timestamp has no timezone: {value!r}. "
            "Supply an explicit UTC offset or Z."
        )

    return parsed.astimezone(timezone.utc).isoformat()


def normalize_event(record: dict[str, Any], event_id: str) -> dict[str, Any]:
    """Validate and normalize one evidence event."""
    if not isinstance(record, dict):
        raise ValueError("Each event must be an object or CSV row")

    missing = [
        field for field in REQUIRED_FIELDS
        if not str(record.get(field, "")).strip()
    ]
    if missing:
        raise ValueError(
            f"Event is missing required fields: {', '.join(missing)}"
        )

    known_fields = {
        "timestamp", "source_type", "action", "source_reference",
        "event_id", "source_id", "account_id", "object_reference",
        "attributes",
    }
    attributes = dict(record.get("attributes") or {})
    attributes.update({
        str(key): value.strip() if isinstance(value, str) else value
        for key, value in record.items()
        if key not in known_fields and value not in (None, "")
    })

    return {
        "event_id": str(record.get("event_id", "")).strip() or event_id,
        "source_id": str(record.get("source_id", "")).strip() or None,
        "timestamp": normalize_timestamp(str(record["timestamp"])),
        "source_type": str(record["source_type"]).strip().lower(),
        "account_id": str(record.get("account_id", "")).strip() or None,
        "action": str(record["action"]).strip(),
        "object_reference": (
            str(record.get("object_reference", "")).strip() or None
        ),
        "source_reference": str(record["source_reference"]).strip(),
        "attributes": attributes,
    }


def parse_events(file_path: str | Path) -> list[dict[str, Any]]:
    """Parse CSV or JSON evidence records into Chronicle's common schema."""
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"Evidence input file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        if path.suffix.lower() == ".csv":
            records = list(csv.DictReader(stream))
        elif path.suffix.lower() == ".json":
            data = json.load(stream)
            records = data.get("events") if isinstance(data, dict) else data

            if not isinstance(records, list):
                raise ValueError(
                    "JSON must contain a list of events or an events list"
                )
        else:
            raise ValueError(f"Unsupported input format: {path.suffix}")

    events = [
        normalize_event(record, f"E{index:04d}")
        for index, record in enumerate(records, start=1)
    ]
    ids = [event["event_id"] for event in events]
    if len(ids) != len(set(ids)):
        raise ValueError("Event IDs must be unique within an evidence input")
    return events
