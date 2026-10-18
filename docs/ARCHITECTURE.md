# Chronicle — Architecture

## Proposed Data Flow
Synthetic Evidence -> SHA-256 Integrity Check -> Python Parser -> Timeline Engine -> Correlation Rules -> Findings and Report -> React Dashboard.

FastAPI is planned as the API between the frontend and analysis engine. Autopsy and Wireshark will support manual examination where feasible.

## Components
- Evidence input: controlled CSV/JSON records.
- Integrity module: SHA-256 hashes and manifest.
- Parser: normalises supported records.
- Timeline engine: chronological ordering.
- Correlation engine: transparent rules linked to source events.
- Report generator: structured investigation report.
- Backend: FastAPI (planned).
- Frontend: React + Vite (planned).

## Proposed Event Fields
 event_id, timestamp, source_type, account_id, action, object_reference, source_reference.

## Status
Proposed architecture; update as components are implemented and tested.
