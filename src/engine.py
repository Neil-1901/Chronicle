import json
from time import perf_counter
from pathlib import Path
from typing import Any

from src.correlation import (
    detect_dns_query_response,
    detect_failed_logins_then_success,
    detect_login_then_file_activity,
    detect_staging_then_transfer,
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
    case_metadata: dict[str, Any] | None = None,
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

    run_started = perf_counter()
    # Keep generated artifacts outside the input evidence directory.
    manifest_path = report_path.parent / f"{case_id}_manifest.csv"
    stage_started = perf_counter()
    create_manifest(evidence_root, manifest_path, (case_metadata or {}).get("additional_files"))

    with manifest_path.open("r", encoding="utf-8", newline="") as stream:
        import csv
        evidence_manifest = list(csv.DictReader(stream))
    intake_seconds = perf_counter() - stage_started

    stage_started = perf_counter()
    events = parse_events(events_path)
    for event in events:
        if not event.get("source_id"):
            event["source_id"] = events_path.name
    parse_seconds = perf_counter() - stage_started
    examination_stage = None
    examination = (case_metadata or {}).get("examination")
    if examination:
        stage_started = perf_counter()
        manifest_by_path = {item["relative_path"]: item for item in evidence_manifest}
        capture_manifest = manifest_by_path.get(examination["capture_path"])
        frame_numbers = [
            (event.get("attributes") or {}).get("frame_number") for event in events
        ]
        packet_checks = {
            "capture_present_in_manifest": capture_manifest is not None,
            "capture_digest_matches_export": bool(capture_manifest) and capture_manifest.get("sha256") == examination["capture_sha256"],
            "all_observations_reference_capture_digest": all(
                (event.get("attributes") or {}).get("capture_sha256") == examination["capture_sha256"]
                for event in events
            ),
            "frame_numbers_unique_and_in_range": (
                len(frame_numbers) == len(set(frame_numbers))
                and all(isinstance(value, int) and 1 <= value <= examination["frame_count"] for value in frame_numbers)
            ),
            "source_references_match_frame_numbers": all(
                event.get("source_reference") == f"{examination['capture_path']}#frame={(event.get('attributes') or {}).get('frame_number')}"
                for event in events
            ),
            "observation_count_matches_capture_frames": len(events) == examination["frame_count"],
        }
        if not all(packet_checks.values()):
            failed = ", ".join(key for key, valid in packet_checks.items() if not valid)
            raise ValueError(f"Packet observation provenance validation failed: {failed}")
        examination_stage = {
            "stage_id": "packet_provenance",
            "name": "Packet export provenance validation",
            "status": "complete",
            "input": {"capture_path": examination["capture_path"], "observation_count": len(events)},
            "output": {"checks": packet_checks, "frame_count": examination["frame_count"], "capture_sha256": capture_manifest["sha256"]},
            "duration_seconds": round(perf_counter() - stage_started, 6),
            "note": "Chronicle validates the exported observations against the current capture fingerprint and packet references. tcpdump/Wireshark performed packet examination; Chronicle does not decode PCAP payloads.",
        }
    stage_started = perf_counter()
    timeline = build_timeline(events)
    timeline_seconds = perf_counter() - stage_started
    stage_started = perf_counter()
    findings = (
        detect_failed_logins_then_success(timeline)
        + detect_login_then_file_activity(timeline)
        + detect_staging_then_transfer(timeline)
        + detect_dns_query_response(timeline)
    )
    correlation_seconds = perf_counter() - stage_started

    rules = [
        {"rule_id": "CORR-001", "name": "Repeated login failures followed by success", "parameters": {"threshold": 3, "window_minutes": 10}, "match_count": sum(f["rule_id"] == "CORR-001" for f in findings)},
        {"rule_id": "CORR-002", "name": "File activity after successful login", "parameters": {"window_minutes": 10}, "match_count": sum(f["rule_id"] == "CORR-002" for f in findings)},
        {"rule_id": "CORR-003", "name": "File archive followed by network upload", "parameters": {"window_minutes": 15, "same_account": True, "compatible_host": True}, "match_count": sum(f["rule_id"] == "CORR-003" for f in findings)},
        {"rule_id": "CORR-004", "name": "DNS query and response share a transaction", "parameters": {"same_transaction_id": True, "reversed_endpoints": True}, "match_count": sum(f["rule_id"] == "CORR-004" for f in findings)},
    ]

    stages = [
        {"stage_id": "intake_integrity", "name": "Evidence intake and fingerprinting", "status": "complete", "input": {"evidence_directory": evidence_root.name}, "output": {"file_count": len(evidence_manifest), "files": evidence_manifest}, "duration_seconds": round(intake_seconds, 6), "note": "SHA-256 fingerprints were calculated for this run. No trusted pre-existing digest was supplied, so historical integrity is not verified."},
        {"stage_id": "parsing", "name": "Parsing and normalization", "status": "complete", "input": {"path": events_path.name, "format": events_path.suffix.lower()}, "output": {"event_count": len(events), "rejected_count": 0, "source_ids": sorted({e.get("source_id") for e in events if e.get("source_id")})}, "duration_seconds": round(parse_seconds, 6)},
        {"stage_id": "timeline", "name": "Timeline reconstruction", "status": "complete", "input": {"event_count": len(events)}, "output": {"event_count": len(timeline), "start": timeline[0]["timestamp"] if timeline else None, "end": timeline[-1]["timestamp"] if timeline else None}, "duration_seconds": round(timeline_seconds, 6)},
        {"stage_id": "correlation", "name": "Rule-based correlation", "status": "complete", "input": {"event_count": len(timeline)}, "output": {"rule_count": len(rules), "match_count": len(findings), "rules": rules}, "duration_seconds": round(correlation_seconds, 6)},
        {"stage_id": "report", "name": "Report generation", "status": "complete", "input": {"findings": len(findings)}, "output": {"format": "JSON", "path": report_path.name}, "duration_seconds": 0.0},
    ]
    if examination_stage:
        stages.insert(2, examination_stage)
    report_started = perf_counter()
    report = generate_report(
        case_id=case_id,
        evidence_manifest=evidence_manifest,
        timeline=timeline,
        findings=findings,
        output_path=report_path,
    )
    report_seconds = perf_counter() - report_started
    stages[-1]["duration_seconds"] = round(report_seconds, 6)

    report["pipeline"] = stages
    metadata = case_metadata or {}
    report["case_name"] = metadata.get("name", case_id)
    report["case_kind"] = metadata.get("kind", "synthetic")
    report["scenario"] = metadata.get("scenario", "")
    report["event_count"] = len(timeline)
    report["processing_seconds"] = round(perf_counter() - run_started, 6)
    report["evidence_summary"]["integrity_status"] = (
        "current-run capture fingerprint matches the export; no trusted external baseline supplied"
        if examination else "fingerprinted; no trusted reference digest supplied"
    )
    source_record_counts = {}
    for event in timeline:
        source_id = event.get("source_id") or events_path.name
        source_record_counts[source_id] = source_record_counts.get(source_id, 0) + 1
    sources = [
        {**source, "input_file": events_path.name,
         "record_count": source_record_counts.get(source["source_id"], 0)}
        for source in metadata.get("sources", [])
    ]
    report["evidence_summary"]["source_count"] = len(source_record_counts)
    report["evidence_summary"]["sources"] = sources
    report["evidence_summary"]["source_record_counts"] = source_record_counts
    report["evidence_summary"]["event_source_ids"] = sorted(source_record_counts)
    report["evidence_summary"]["artifact_metadata"] = metadata.get("artifact_metadata", {})
    if examination:
        report["examination"] = examination
    report["event_type_counts"] = {
        key: sum(event.get("source_type") == key for event in timeline)
        for key in sorted({event.get("source_type") for event in timeline})
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Validate the report after its case metadata and full timeline have been
    # added. Correlation references must resolve to records in this run.
    validation_started = perf_counter()
    event_ids = {event.get("event_id") for event in timeline}
    registered_source_ids = {
        source.get("source_id") for source in metadata.get("sources", [])
        if source.get("source_id")
    }
    finding_event_ids = {
        event_id
        for finding in findings
        for event_id in finding.get("supporting_event_ids", [])
    }
    checks = {
        "case_id_matches": report.get("case_id") == case_id,
        "timeline_count_matches": len(report.get("timeline", [])) == len(timeline),
        "finding_count_matches": len(report.get("findings", [])) == len(findings),
        "finding_event_references_resolve": finding_event_ids <= event_ids,
        "timeline_events_have_source_references": all(event.get("source_id") and event.get("source_reference") for event in timeline),
        "event_sources_are_registered": (
            all(event.get("source_id") in registered_source_ids for event in timeline)
            if registered_source_ids else all(event.get("source_id") for event in timeline)
        ),
        "finding_source_references_resolve": all(
            record.get("source_reference") in {event.get("source_reference") for event in timeline}
            for finding in findings for record in finding.get("supporting_records", [])
        ),
    }
    if not all(checks.values()):
        raise ValueError("Generated report failed validation: " + ", ".join(k for k, ok in checks.items() if not ok))

    validation_stage = {
        "stage_id": "validation",
        "name": "Report and finding validation",
        "status": "complete",
        "input": {"report_path": report_path.name, "event_count": len(timeline), "finding_count": len(findings)},
        "output": {"checks": checks, "finding_event_reference_count": len(finding_event_ids)},
        "duration_seconds": round(perf_counter() - validation_started, 6),
    }
    report["pipeline"].append(validation_stage)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # Read back the artifact that the API and download controls will serve.
    saved_report = json.loads(report_path.read_text(encoding="utf-8"))
    saved_report_valid = (
        saved_report.get("case_id") == case_id
        and len(saved_report.get("timeline", [])) == len(timeline)
        and len(saved_report.get("findings", [])) == len(findings)
        and saved_report.get("pipeline", [])[-1].get("stage_id") == "validation"
    )
    if not saved_report_valid:
        raise ValueError("Serialized report failed read-back validation")
    validation_stage["output"]["saved_report_readback"] = saved_report_valid
    report["processing_seconds"] = round(perf_counter() - run_started, 6)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    final_saved_report = json.loads(report_path.read_text(encoding="utf-8"))
    if (
        not final_saved_report.get("pipeline", [])[-1].get("output", {}).get("saved_report_readback")
        or final_saved_report.get("processing_seconds") != report["processing_seconds"]
    ):
        raise ValueError("Final serialized report failed read-back validation")

    return report
