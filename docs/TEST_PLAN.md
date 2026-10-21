# Validation plan and verified scope

The current automated suite covers parser inputs and timestamps, duplicate stable IDs, timeline ordering, four correlation rules, hash calculation, manifests, report serialization, the original six-event fixture, Glasshouse event count/IDs, capture/export provenance validation, report-to-source traceability, and API case selection/error response. Run `.venv/bin/python evaluation/run_evaluation.py` for the current test result.

Run:

```bash
.venv/bin/python evaluation/run_evaluation.py
cd frontend && npm run build
```

The test report states actual totals. These checks do not establish real-world forensic accuracy, validate the truth of synthetic scenario labels, or test native PCAP parsing. This pass also exercised all three cases in the browser, including finding-to-frame navigation, the evidence ledger, report, and separate synthetic case runs.
