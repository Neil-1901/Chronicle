from datetime import datetime
from typing import Any


def _parse_timestamp(value: str) -> datetime:
    """Parse a timezone-aware ISO-8601 timestamp."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Event timestamp is required")

    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"Invalid event timestamp: {value!r}") from exc

    if parsed.tzinfo is None:
        raise ValueError(f"Event timestamp has no timezone: {value!r}")

    return parsed


def detect_failed_logins_then_success(
    events: list[dict[str, Any]],
    threshold: int = 3,
    window_minutes: int = 10,
) -> list[dict[str, Any]]:
    """Find repeated login failures followed by success for the same account.

    Expected normalized action values are 'login_failure' and 'login_success'.
    Findings are investigative leads, not proof of user identity.
    """
    if threshold < 1:
        raise ValueError("threshold must be at least 1")
    if window_minutes < 1:
        raise ValueError("window_minutes must be at least 1")

    parsed_events = []
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("Every event must be a dictionary")

        timestamp = _parse_timestamp(event.get("timestamp"))
        parsed_events.append((timestamp, event))

    parsed_events.sort(key=lambda item: item[0])
    findings = []

    for success_time, success in parsed_events:
        if success.get("action") != "login_success":
            continue

        account_id = success.get("account_id")
        if not account_id:
            continue

        window_start = success_time.timestamp() - window_minutes * 60
        failures = [
            event
            for event_time, event in parsed_events
            if event.get("action") == "login_failure"
            and event.get("account_id") == account_id
            and window_start <= event_time.timestamp() < success_time.timestamp()
        ]

        if len(failures) < threshold:
            continue

        evidence_ids = [
            str(event["event_id"])
            for event in failures
            if event.get("event_id") is not None
        ]
        if success.get("event_id") is not None:
            evidence_ids.append(str(success["event_id"]))

        findings.append({
            "rule_id": "CORR-001",
            "severity": "medium",
            "title": "Repeated login failures followed by success",
            "account_id": account_id,
            "supporting_event_ids": evidence_ids,
            "failure_count": len(failures),
            "window_minutes": window_minutes,
            "explanation": (
                f"{len(failures)} failed login events were followed by a "
                f"successful login for the same account within "
                f"{window_minutes} minutes. This is suspicious activity "
                "to investigate, not proof of who performed the login."
            ),
        })

    return findings



def detect_login_then_file_activity(
    events: list[dict[str, Any]],
    window_minutes: int = 10,
) -> list[dict[str, Any]]:
    """Find file activity shortly after a successful login for the same account."""
    if window_minutes < 1:
        raise ValueError("window_minutes must be at least 1")

    parsed_events = []
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("Every event must be a dictionary")
        parsed_events.append((_parse_timestamp(event.get("timestamp")), event))

    parsed_events.sort(key=lambda item: item[0])
    findings = []

    for login_time, login in parsed_events:
        if login.get("action") != "login_success":
            continue

        account_id = login.get("account_id")
        if not account_id:
            continue

        login_epoch = login_time.timestamp()
        matching_activity = [
            event
            for event_time, event in parsed_events
            if event.get("account_id") == account_id
            and str(event.get("source_type", "")).lower() == "file_activity"
            and str(event.get("action", "")).lower()
                in {"file_opened", "file_modified", "file_deleted", "file_created"}
            and login_epoch < event_time.timestamp()
            <= login_epoch + window_minutes * 60
        ]

        if not matching_activity:
            continue

        supporting_events = [login, *matching_activity]
        findings.append({
            "rule_id": "CORR-002",
            "severity": "low",
            "title": "File activity after successful login",
            "account_id": account_id,
            "supporting_event_ids": [
                str(event["event_id"])
                for event in supporting_events
                if event.get("event_id") is not None
            ],
            "source_references": [
                str(event["source_reference"])
                for event in supporting_events
                if event.get("source_reference") is not None
            ],
            "window_minutes": window_minutes,
            "explanation": (
                f"A successful login was followed by {len(matching_activity)} "
                f"file-activity event(s) for the same account within "
                f"{window_minutes} minutes. This temporal association is an "
                "investigative lead; it does not establish who performed the "
                "actions, whether the activity was authorised, or whether "
                "the login caused the file activity."
            ),
            "limitation": (
                "The rule relies on account identifiers and timestamps in "
                "the supplied records. Shared accounts, inaccurate clocks, "
                "or incomplete logs may produce misleading associations."
            ),
        })

    return findings
