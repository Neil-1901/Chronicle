import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def generate_report(
    case_id: str,
    evidence_manifest: list[dict[str, Any]],
    timeline: list[dict[str, Any]],
    findings: list[dict[str, Any]],
    output_path: str | Path,
) -> dict[str, Any]:
    """Generate and save a structured JSON forensic investigation report."""
    if not isinstance(case_id, str) or not case_id.strip():
        raise ValueError("case_id must be a non-empty string")

    for name, value in (
        ("evidence_manifest", evidence_manifest),
        ("timeline", timeline),
        ("findings", findings),
    ):
        if not isinstance(value, list):
            raise ValueError(f"{name} must be a list")

    report = {
        "report_version": "1.0",
        "case_id": case_id.strip(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_summary": {
            "file_count": len(evidence_manifest),
            "files": evidence_manifest,
        },
        "timeline": timeline,
        "findings": findings,
        "limitations": [
            "This report is generated from the evidence records supplied to Chronicle.",
            "A correlation finding is an investigative lead, not proof of identity or intent.",
            "Timestamps and account identifiers depend on the accuracy of the source records.",
            "Hash values support integrity checking but do not establish that evidence was authentic before collection.",
        ],
    }

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return report
