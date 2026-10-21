from __future__ import annotations

import json
import sys
import unittest
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Ensure project modules such as src.engine are importable when this
# script is launched directly from the evaluation directory.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
TESTS_DIR = ROOT / "tests"
OUTPUT_DIR = ROOT / "outputs"
DOCS_DIR = ROOT / "docs"


class EvaluationResult(unittest.TestResult):
    """Collect individual outcomes from the actual unittest execution."""

    def __init__(self):
        super().__init__()
        self.records = []

    def startTest(self, test):
        super().startTest(test)
        self._current_test = test

    def addSuccess(self, test):
        super().addSuccess(test)
        self.records.append({
            "test": test.id(),
            "status": "PASS",
            "detail": "",
        })

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.records.append({
            "test": test.id(),
            "status": "FAIL",
            "detail": self._exc_info_to_string(err, test),
        })

    def addError(self, test, err):
        super().addError(test, err)
        self.records.append({
            "test": test.id(),
            "status": "ERROR",
            "detail": self._exc_info_to_string(err, test),
        })

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.records.append({
            "test": test.id(),
            "status": "SKIP",
            "detail": reason,
        })

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.records.append({
            "test": test.id(),
            "status": "EXPECTED_FAILURE",
            "detail": self._exc_info_to_string(err, test),
        })

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.records.append({
            "test": test.id(),
            "status": "UNEXPECTED_SUCCESS",
            "detail": "Test was marked expected to fail but succeeded.",
        })


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    loader = unittest.defaultTestLoader
    suite = loader.discover(
        start_dir=str(TESTS_DIR),
        pattern="test_*.py",
        top_level_dir=str(TESTS_DIR),
    )

    result = EvaluationResult()
    started_at = datetime.now(timezone.utc)
    runner = unittest.TextTestRunner(
        stream=sys.stdout,
        verbosity=2,
        resultclass=lambda *args, **kwargs: result,
    )
    runner.run(suite)
    finished_at = datetime.now(timezone.utc)

    records = sorted(result.records, key=lambda item: item["test"])
    counts = defaultdict(int)

    for record in records:
        counts[record["status"]] += 1

    total = len(records)
    passed = counts["PASS"]
    failed = counts["FAIL"]
    errors = counts["ERROR"]
    skipped = counts["SKIP"]

    status = "PASS" if not (
        failed or errors or counts["UNEXPECTED_SUCCESS"]
    ) else "FAIL"

    report = {
        "project": "Chronicle",
        "evaluation_type": "Automated unit-test evaluation",
        "scope": (
            "Existing Python unittest suite. Results apply only to the "
            "executed tests and do not establish real-world forensic accuracy."
        ),
        "status": status,
        "started_at_utc": started_at.isoformat(),
        "finished_at_utc": finished_at.isoformat(),
        "duration_seconds": round(
            (finished_at - started_at).total_seconds(), 4
        ),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "skipped": skipped,
            "expected_failures": counts["EXPECTED_FAILURE"],
            "unexpected_successes": counts["UNEXPECTED_SUCCESS"],
        },
        "tests": records,
    }

    json_path = OUTPUT_DIR / "evaluation_report.json"
    json_path.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    groups = defaultdict(list)
    for record in records:
        parts = record["test"].split(".")
        module = parts[0] if parts else "unknown"
        groups[module].append(record)

    lines = [
        "# Chronicle — Automated Evaluation Report",
        "",
        f"**Overall result:** {status}",
        "",
        f"- **Started (UTC):** {started_at.isoformat()}",
        f"- **Finished (UTC):** {finished_at.isoformat()}",
        f"- **Duration:** {report['duration_seconds']} seconds",
        f"- **Tests executed:** {total}",
        f"- **Passed:** {passed}",
        f"- **Failed:** {failed}",
        f"- **Errors:** {errors}",
        f"- **Skipped:** {skipped}",
        "",
        "## Evaluation method",
        "",
        "This report is generated by executing the repository's existing "
        "Python `unittest` suite. Each listed result comes from that run. "
        "Run `python evaluation/run_evaluation.py` from the repository root "
        "to reproduce the evaluation.",
        "",
        "## Results by test module",
        "",
        "| Test module | Passed | Failed | Errors | Skipped |",
        "|---|---:|---:|---:|---:|",
    ]

    for module in sorted(groups):
        items = groups[module]
        lines.append(
            f"| `{module}` "
            f"| {sum(x['status'] == 'PASS' for x in items)} "
            f"| {sum(x['status'] == 'FAIL' for x in items)} "
            f"| {sum(x['status'] == 'ERROR' for x in items)} "
            f"| {sum(x['status'] == 'SKIP' for x in items)} |"
        )

    lines.extend(["", "## Individual test results", ""])

    for module in sorted(groups):
        lines.extend([f"### `{module}`", ""])
        for record in groups[module]:
            lines.append(
                f"- **{record['status']}** — `{record['test']}`"
            )
            if record["detail"]:
                detail = record["detail"].strip().splitlines()
                if detail:
                    lines.append(f"  - Detail: `{detail[-1][:300]}`")
        lines.append("")

    lines.extend([
        "## Evaluation scope and limitations",
        "",
        "- Passing tests show that the tested conditions behaved as expected "
        "during this run; they do not prove the absence of defects.",
        "- This is a unit-test evaluation, not a benchmark of forensic "
        "attribution accuracy against a labelled real-world dataset.",
        "- It does not independently validate the authenticity or provenance "
        "of the supplied evidence or public packet capture.",
        "- It does not establish a real person's identity, intent, or "
        "culpability.",
        "- The report records only tests discovered and executed by this "
        "runner. Manual tool demonstrations and end-to-end browser checks "
        "must be documented separately if performed.",
        "",
        "## Reproducibility",
        "",
        "Run from the Chronicle repository root:",
        "",
        "```bash",
        ".venv/bin/python evaluation/run_evaluation.py",
        "```",
        "",
        f"Machine-readable results: `{json_path.relative_to(ROOT)}`",
        "",
    ])

    markdown_path = DOCS_DIR / "evaluation-report.md"
    markdown_path.write_text("\n".join(lines), encoding="utf-8")

    print("\n=== EVALUATION ARTIFACTS ===")
    print(f"JSON:     {json_path.relative_to(ROOT)}")
    print(f"Markdown: {markdown_path.relative_to(ROOT)}")
    print(f"Result: {status} — {passed}/{total} passed")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
