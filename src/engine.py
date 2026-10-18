import json
from pathlib import Path
from typing import Any

from src.correlation import (
    detect_failed_logins_then_success,
    detect_login_then_file_activity,
)
from src.manifest import create_manifest
from src.parsers import parse_events
from src.report import generate_report
from src.timeline import build_timeline


def run_investigation(
    case_id: str,
    evidence_dir: str | Path,
    events_file: str | Path,
    output_report: str | Path,
) -> dict[str, Any]:
    """Run Chronicle's investigation pipeline on supplied evidence."""
    evidence_root = Path(evidence_dir)
    events_path = Path(events_file)
    report_path = Path(output_report)

    if not evidence_root.is_dir():
        raise FileNotFoundError(
            f"Evidence directory not found: {evidence_root}"
        )

    if not events_path.is_file():
        raise FileNotFoundError(
            f"Events file not found: {events_path}"
        )

    # Keep the generated manifest outside the evidence directory.
    manifest_path = report_path.parent / f"{case_id}_manifest.csv"
    create_manifest(evidence_root, manifest_path)

    with manifest_path.open("r", encoding="utf-8", newline="") as stream:
        import csv
        evidence_manifest = list(csv.DictReader(stream))

    events = parse_events(events_path)
    timeline = build_timeline(events)
    findings = (
        detect_failed_logins_then_success(timeline)
        + detect_login_then_file_activity(timeline)
    )

    report = generate_report(
        case_id=case_id,
        evidence_manifest=evidence_manifest,
        timeline=timeline,
        findings=findings,
        output_path=report_path,
    )

    return report
