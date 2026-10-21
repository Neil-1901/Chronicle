from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CASES = {
    "CHRONICLE-DEMO-001": {
        "case_id": "CHRONICLE-DEMO-001",
        "name": "Six-event regression demonstration",
        "kind": "synthetic",
        "scenario": "A compact fabricated authentication and file-activity sequence used to preserve the original demo behavior.",
        "evidence_dir": ROOT / "data" / "raw",
        "events_file": ROOT / "data" / "raw" / "events.csv",
        "sources": [
            {"source_id": "events.csv", "name": "Synthetic authentication and file event fixture", "format": "CSV", "provenance": "Fabricated academic test records"}
        ],
    },
    "OPERATION-GLASSHOUSE": {
        "case_id": "OPERATION-GLASSHOUSE",
        "name": "Operation Glasshouse",
        "kind": "synthetic",
        "scenario": "A simulated review of suspected unauthorized access and possible file staging and outbound transfer. Competing benign explanations are included; no person is attributed.",
        "evidence_dir": ROOT / "data" / "cases" / "operation-glasshouse",
        "events_file": ROOT / "data" / "cases" / "operation-glasshouse" / "events.csv",
        "sources": [
            {"source_id": "AUTH-01", "name": "Authentication audit export", "format": "CSV rows in events.csv", "provenance": "Synthetic source records"},
            {"source_id": "AUTH-02", "name": "Service authentication audit export", "format": "CSV rows in events.csv", "provenance": "Synthetic source records"},
            {"source_id": "ENDPOINT-01", "name": "Endpoint file activity export", "format": "CSV rows in events.csv", "provenance": "Synthetic source records"},
            {"source_id": "ENDPOINT-02", "name": "File server activity export", "format": "CSV rows in events.csv", "provenance": "Synthetic source records"},
            {"source_id": "NETWORK-01", "name": "Proxy and network observation export", "format": "CSV rows in events.csv", "provenance": "Synthetic source records; no PCAP payload analysis"},
            {"source_id": "NETWORK-02", "name": "Backup network observation export", "format": "CSV rows in events.csv", "provenance": "Synthetic source records; no PCAP payload analysis"},
        ],
    },
    "WIRESHARK-PRACTICE-001": {
        "case_id": "WIRESHARK-PRACTICE-001",
        "name": "HTTP Capture Practice Examination",
        "kind": "public-sample",
        "scenario": "Examine a supplied public HTTP/DNS practice capture, preserve its packet references, and report only what the capture and supplied Wireshark exhibits support. The sample is not evidence from C-001 or Operation Glasshouse.",
        "evidence_dir": ROOT / "data" / "cases" / "wireshark-practice",
        "events_file": ROOT / "data" / "cases" / "wireshark-practice" / "http-cap-observations.json",
        "sources": [
            {"source_id": "HTTP-CAP-01", "name": "Public HTTP practice capture", "format": "PCAP 2.4 / Ethernet", "provenance": "Public Wireshark sample capture contributed by Shreya; not incident-acquired evidence", "input_file": "evidence/captures/http.cap", "artifact_type": "original public sample", "examination_status": "examined with tcpdump; Wireshark observations preserved in supplied screenshots"},
        ],
        "additional_files": [
            {"relative_path": "evidence/captures/http.cap", "path": ROOT / "evidence" / "captures" / "http.cap"},
            {"relative_path": "evidence/screenshots/wireshark-http.png", "path": ROOT / "evidence" / "screenshots" / "wireshark-http.png"},
            {"relative_path": "evidence/screenshots/wireshark-dns.png", "path": ROOT / "evidence" / "screenshots" / "wireshark-dns.png"},
            {"relative_path": "docs/investigation/wireshark-analysis.md", "path": ROOT / "docs" / "investigation" / "wireshark-analysis.md"},
        ],
        "artifact_metadata": {
            "http-cap-observations.json": {"artifact_type": "derived structured packet-summary export", "provenance": "Generated from the public capture using the documented tcpdump extractor; Wireshark screenshot annotations are individually attributed."},
            "evidence/captures/http.cap": {"artifact_type": "original public sample capture", "provenance": "Public Wireshark practice sample; source is identified in the supplied examination notes. No incident acquisition is claimed."},
            "evidence/screenshots/wireshark-http.png": {"artifact_type": "visual examination exhibit", "provenance": "Wireshark HTTP-filter screenshot supplied by Shreya; used only for the observations attributed to this exhibit."},
            "evidence/screenshots/wireshark-dns.png": {"artifact_type": "visual examination exhibit", "provenance": "Wireshark DNS-filter screenshot supplied by Shreya; used only for the observations attributed to this exhibit."},
            "docs/investigation/wireshark-analysis.md": {"artifact_type": "examiner notes", "provenance": "Analysis notes supplied with Shreya’s practice-capture materials; reconciled against tcpdump output and screenshots."},
        },
        "examination": {
            "capture_path": "evidence/captures/http.cap",
            "capture_filename": "http.cap",
            "capture_sha256": "25a72bdf10339f2c29916920c8b9501d294923108de8f29b19aba7cc001ab60d",
            "frame_count": 43,
            "source_id": "HTTP-CAP-01",
            "export_path": "data/cases/wireshark-practice/http-cap-observations.json",
            "method": "Documented data/extract_http_cap.py invokes tcpdump for per-frame summary and ASCII HTTP header extraction. Supplied Wireshark screenshots provide separately attributed HTTP/DNS filter observations.",
            "tool": "tcpdump 4.99.1 (export records tool version); Wireshark 4.6.9 is reported in Shreya’s notes, not independently installed/verified here.",
            "timezone_note": "PCAP epoch values normalized as UTC; original capture timezone metadata is not independently established.",
            "limitations": ["Public practice sample, not incident evidence.", "No user identity or malicious intent is established.", "TCP stream reconstruction and complete protocol reassembly are not performed by Chronicle.", "Decoder classifications differ for some adjacent TCP segments; tcpdump summaries and Wireshark screenshot annotations are both retained with provenance."],
        },
    },
}


def list_cases() -> list[dict]:
    return [
        {key: value for key, value in case.items() if key not in {"evidence_dir", "events_file", "additional_files"}}
        for case in CASES.values()
    ]
