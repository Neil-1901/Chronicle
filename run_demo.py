from pathlib import Path
from src.engine import run_investigation

ROOT = Path(__file__).resolve().parent

report = run_investigation(
    case_id="CHRONICLE-DEMO-001",
    evidence_dir=ROOT / "data" / "raw",
    events_file=ROOT / "data" / "raw" / "events.csv",
    output_report=ROOT / "outputs" / "demo_report.json",
)

print("Investigation completed.")
print(f"Case ID: {report.get('case_id', 'CHRONICLE-DEMO-001')}")
print(f"Report: {ROOT / 'outputs' / 'demo_report.json'}")

