# Backend modules

- `api.py`: local FastAPI case, report, evaluation, and investigation endpoints.
- `cases.py`: registry for the original six-event case and Operation Glasshouse.
- `engine.py`: manifest, parsing, timeline, correlation, and report orchestration.
- `parsers.py`, `timeline.py`: event normalization and chronological reconstruction.
- `correlation.py`: the three documented rules and supporting-record references.
- `hashing.py`, `manifest.py`: SHA-256 fingerprints and file inventory.
- `report.py`: JSON report generation.

See [architecture](../docs/ARCHITECTURE.md) for actual runtime data flow.
