# Operation Glasshouse

## Scenario

Operation Glasshouse is a fully synthetic academic exercise about suspected account access and possible file staging followed by network transfer. It does not describe a real incident and does not attribute activity to a real person.

The deterministic generator creates 240 events across authentication, endpoint/file activity, and network-observation categories. The input includes a three-failure/login-success sequence, file access and an archive record, and a nearby upload observation. It also includes a scheduled service-account backup that triggers the same archive-to-upload rule. That second match is a deliberate competing explanation.

## How to reproduce

```bash
.venv/bin/python data/generate_glasshouse.py
.venv/bin/python evaluation/run_evaluation.py
```

The generator uses seed `1901`, stable `GH-E####` event IDs, stable source IDs, fixed dates, and documented source references. It writes event input to `data/cases/operation-glasshouse/events.csv`. The generator labels are stored separately in `data/evaluation/operation-glasshouse-ground-truth.json` and are not loaded by the investigation engine.

## Interpretation

The resulting rules identify associations in the supplied fields. The second CORR-003 match demonstrates that a temporal and account/host relationship can describe a benign backup. Neither sequence proves that the listed account corresponds to a human, that an event was unauthorized, or that uploaded data came from an archive.

The original six-event demo remains in `data/raw/events.csv` and is independently selectable. Shreya’s public Wireshark sample and the C-001 synthetic-note exhibit are separate reference materials, not Glasshouse sources.
