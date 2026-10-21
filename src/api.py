from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.engine import run_investigation
from src.cases import CASES, list_cases

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "raw"
OUTPUT_DIR = ROOT / "outputs"

app = FastAPI(
    title="Chronicle Forensic API",
    description="API for a simulated digital forensic investigation.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "application": "Chronicle"}


@app.get("/api/cases")
def get_cases():
    return {"cases": list_cases()}


@app.get("/api/report")
def get_report(case_id: str | None = None):
    legacy_request = case_id is None
    case_id = case_id or "CHRONICLE-DEMO-001"
    if case_id not in CASES:
        raise HTTPException(status_code=404, detail="Case not found.")
    report_path = OUTPUT_DIR / f"{case_id}_report.json"
    if legacy_request and case_id == "CHRONICLE-DEMO-001" and not report_path.is_file():
        report_path = OUTPUT_DIR / "demo_report.json"
    if not report_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Report not found. Run an investigation first.",
        )

    import json
    return json.loads(report_path.read_text(encoding="utf-8"))


@app.get("/api/evaluation")
def get_evaluation():
    import json

    evaluation_path = OUTPUT_DIR / "evaluation_report.json"
    if not evaluation_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Evaluation report not found. Run evaluation/run_evaluation.py first.",
        )

    try:
        return json.loads(evaluation_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=500,
            detail="Evaluation report could not be read.",
        ) from exc


@app.post("/api/investigate/{case_id}")
def investigate_case(case_id: str):
    if case_id not in CASES:
        raise HTTPException(status_code=404, detail="Case not found.")
    case = CASES[case_id]
    events_file = case["events_file"]
    if not events_file.is_file():
        raise HTTPException(
            status_code=404,
            detail="Synthetic events file not found.",
        )

    try:
        return run_investigation(
            case_id=case_id,
            evidence_dir=case["evidence_dir"],
            events_file=events_file,
            output_report=OUTPUT_DIR / f"{case_id}_report.json",
            case_metadata=case,
        )
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/investigate")
def investigate_original_demo():
    return investigate_case("CHRONICLE-DEMO-001")
