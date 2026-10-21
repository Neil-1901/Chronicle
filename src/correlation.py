from datetime import datetime
from typing import Any


def _supporting_records(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "event_id": event.get("event_id"),
            "timestamp": event.get("timestamp"),
            "source_id": event.get("source_id"),
            "source_reference": event.get("source_reference"),
            "source_type": event.get("source_type"),
            "action": event.get("action"),
        }
        for event in events
    ]


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
            "supporting_records": _supporting_records([*failures, success]),
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
            "supporting_records": _supporting_records(supporting_events),
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


def detect_staging_then_transfer(
    events: list[dict[str, Any]], window_minutes: int = 15
) -> list[dict[str, Any]]:
    """Link a file archive event to a later network transfer for one account/host."""
    if window_minutes < 1:
        raise ValueError("window_minutes must be at least 1")

    parsed = [(_parse_timestamp(e.get("timestamp")), e) for e in events]
    parsed.sort(key=lambda item: item[0])
    findings: list[dict[str, Any]] = []
    archives = [(when, e) for when, e in parsed if e.get("action") == "archive_created"]
    transfers = [(when, e) for when, e in parsed if e.get("action") == "network_upload"]

    for archive_time, archive in archives:
        archive_host = (archive.get("attributes") or {}).get("host")
        matching = []
        for transfer_time, transfer in transfers:
            transfer_host = (transfer.get("attributes") or {}).get("host")
            same_identity = archive.get("account_id") == transfer.get("account_id")
            same_host = not archive_host or not transfer_host or archive_host == transfer_host
            elapsed = (transfer_time - archive_time).total_seconds()
            if same_identity and same_host and 0 < elapsed <= window_minutes * 60:
                matching.append(transfer)
        if not matching:
            continue
        records = [archive, *matching]
        findings.append({
            "rule_id": "CORR-003",
            "severity": "medium",
            "title": "File archive followed by network upload",
            "account_id": archive.get("account_id"),
            "supporting_event_ids": [str(e["event_id"]) for e in records if e.get("event_id")],
            "supporting_records": _supporting_records(records),
            "window_minutes": window_minutes,
            "explanation": "An archive creation was followed by a recorded network upload for the same account and compatible host within the rule window.",
            "alternative_explanations": [
                "The archive and transfer may be part of an authorised backup, sync, or software workflow.",
                "Account and host labels are synthetic log fields and do not establish the human operator or causation.",
            ],
            "limitation": "This rule links event records by account, host, and time. It does not inspect packet payloads or prove that the uploaded bytes came from the archive.",
        })
    return findings


def detect_dns_query_response(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Link a DNS response to a query by transaction ID and reversed endpoints."""
    indexed = {event.get("event_id"): event for event in events if event.get("event_id")}
    findings = []
    for response in events:
        attrs = response.get("attributes") or {}
        query_id = attrs.get("paired_query_event_id")
        query = indexed.get(query_id)
        if response.get("action") != "dns_response" or not query or query.get("action") != "dns_query":
            continue
        query_attrs = query.get("attributes") or {}
        if not attrs.get("dns_transaction_id") or attrs.get("dns_transaction_id") != query_attrs.get("dns_transaction_id"):
            continue
        if (query_attrs.get("source_ip"), query_attrs.get("source_port")) != (attrs.get("destination_ip"), attrs.get("destination_port")):
            continue
        if (query_attrs.get("destination_ip"), query_attrs.get("destination_port")) != (attrs.get("source_ip"), attrs.get("source_port")):
            continue
        records = [query, response]
        findings.append({
            "rule_id": "CORR-004",
            "severity": "informational",
            "title": "DNS query and response share a transaction",
            "supporting_event_ids": [query["event_id"], response["event_id"]],
            "supporting_records": _supporting_records(records),
            "source_references": [event["source_reference"] for event in records],
            "dns_transaction_id": attrs["dns_transaction_id"],
            "query_name": query.get("object_reference"),
            "explanation": "The capture contains a DNS response with the same transaction ID and reversed network endpoints as this recorded query.",
            "alternative_explanations": ["This is consistent with ordinary DNS resolution for the captured web page and does not indicate malicious activity."],
            "limitation": "The transaction match establishes a query/response relationship in this capture only. It does not identify a person, establish domain intent, or prove that later HTTP traffic was caused by the DNS answer.",
        })
    return findings
