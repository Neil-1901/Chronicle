"""Create a source-linked JSON event export from the supplied public PCAP.

Requires tcpdump on PATH. Chronicle consumes this exported JSON; the packet
capture itself is examined by tcpdump (or Wireshark), not parsed by Chronicle.
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CAPTURE = ROOT / "evidence/captures/http.cap"
DEFAULT_OUTPUT = ROOT / "data/cases/wireshark-practice/http-cap-observations.json"
PACKET_LINE = re.compile(r"^(\d+\.\d+) IP (\S+) > (\S+): (.*)$")
ENDPOINT = re.compile(r"^(.+)\.(\d+)$")


def _split_endpoint(value: str) -> tuple[str, int | None]:
    match = ENDPOINT.match(value)
    if not match:
        return value, None
    return match.group(1), int(match.group(2))


def _tcpdump_version(executable: str) -> str:
    output = subprocess.run(
        [executable, "--version"], capture_output=True, text=True, check=True
    ).stdout
    return output.splitlines()[0].strip()


def extract_observations(capture: Path, tcpdump: str | None = None) -> dict:
    executable = tcpdump or shutil.which("tcpdump")
    if not executable:
        raise RuntimeError("tcpdump is required to regenerate the packet observation export")
    capture = capture.resolve()
    if not capture.is_file():
        raise FileNotFoundError(capture)

    digest = hashlib.sha256(capture.read_bytes()).hexdigest()
    summary = subprocess.run(
        [executable, "-nn", "-tt", "-r", str(capture)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    ascii_dump = subprocess.run(
        [executable, "-nn", "-tt", "-A", "-r", str(capture)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    # tcpdump prints one summary line per frame. The sequential index is the
    # PCAP frame number, verified against the supplied Wireshark screenshots.
    packet_headers: dict[int, dict[str, str]] = {}
    frame = 0
    for line in ascii_dump.splitlines():
        match = PACKET_LINE.match(line)
        if match:
            frame += 1
            continue
        if frame and line.startswith(("Host: ", "User-Agent: ")):
            key, value = line.split(":", 1)
            packet_headers.setdefault(frame, {})[key.lower().replace("-", "_")] = value.strip()

    events = []
    for line in summary.splitlines():
        match = PACKET_LINE.match(line)
        if not match:
            continue
        raw_epoch, source, destination, decoded = match.groups()
        frame = len(events) + 1
        source_ip, source_port = _split_endpoint(source)
        destination_ip, destination_port = _split_endpoint(destination)

        dns_query = re.search(r"\b(\d+)\+?\s+\w+\?\s+([^ ]+)", decoded)
        dns_response = re.search(r"\b(\d+)\s+\d+/\d+/\d+\s+", decoded)
        if dns_query:
            action, protocol, transaction_id = "dns_query", "DNS", dns_query.group(1)
            object_reference = dns_query.group(2).rstrip(".")
        elif dns_response:
            action, protocol, transaction_id = "dns_response", "DNS", dns_response.group(1)
            object_reference = None
        elif "HTTP:" in decoded:
            # tcpdump may identify HTTP in TCP segments that Wireshark's
            # supplied display-filter screenshot does not show as HTTP.
            action, protocol, transaction_id = "packet_observed", "TCP", None
            object_reference = f"{destination_ip}:{destination_port}" if destination_port else destination_ip
        else:
            action, protocol, transaction_id = "packet_observed", "TCP", None
            object_reference = f"{destination_ip}:{destination_port}" if destination_port else destination_ip

        timestamp = datetime.fromtimestamp(float(raw_epoch), timezone.utc).isoformat(timespec="microseconds")
        event = {
            "event_id": f"PCAP-E{frame:04d}",
            "source_id": "HTTP-CAP-01",
            "timestamp": timestamp,
            "source_type": "network",
            "action": action,
            "object_reference": object_reference,
            "source_reference": f"evidence/captures/{capture.name}#frame={frame}",
            "attributes": {
                "capture_filename": capture.name,
                "capture_sha256": digest,
                "frame_number": frame,
                "raw_capture_timestamp_epoch": raw_epoch,
                "timestamp_interpretation": "PCAP epoch timestamp converted to UTC; capture timezone metadata was not independently established.",
                "protocol": protocol,
                "source_ip": source_ip,
                "source_port": source_port,
                "destination_ip": destination_ip,
                "destination_port": destination_port,
                "decoded_summary": decoded,
                "extraction_tool": _tcpdump_version(executable),
                "extraction_method": "tcpdump -nn -tt -r; tcpdump -nn -tt -A used to extract visible HTTP Host and User-Agent headers",
                "export_filename": DEFAULT_OUTPUT.name,
                "export_record_reference": f"http-cap-observations.json#events/{frame - 1}",
            },
        }
        if transaction_id is not None:
            event["attributes"]["dns_transaction_id"] = transaction_id
        event["attributes"].update(packet_headers.get(frame, {}))
        if "HTTP:" in decoded:
            event["attributes"]["tcpdump_application_hint"] = decoded.split("HTTP:", 1)[1].strip()
        events.append(event)

    # The supplied Wireshark screenshot records these filtered observations.
    # Preserve the exhibit as the source of this annotation and retain the
    # tcpdump summary separately; the two dissectors classify some TCP
    # segments differently because their HTTP stream handling differs.
    wireshark_observations = {
        4: ("http_request", "HTTP", "/download.html", "GET /download.html HTTP/1.1"),
        18: ("http_request", "HTTP", "/pagead/ads", "GET /pagead/ads?... HTTP/1.1"),
        27: ("http_response", "HTTP", "HTTP/1.1 200 OK", "HTTP/1.1 200 OK (text/html)"),
        38: ("http_response", "HTTP", "HTTP/1.1 200 OK", "HTTP/1.1 200 OK"),
        13: ("dns_query", "DNS", "pagead2.googlesyndication.com", "DNS A query"),
        17: ("dns_response", "DNS", "pagead2.googlesyndication.com", "DNS A query response"),
    }
    for frame, (action, protocol, object_reference, observation) in wireshark_observations.items():
        event = events[frame - 1]
        event["action"] = action
        event["object_reference"] = object_reference
        event["attributes"]["protocol"] = protocol
        event["attributes"]["wireshark_annotation"] = observation
        event["attributes"]["annotation_source"] = "evidence/screenshots/wireshark-http.png" if frame in {4, 18, 27, 38} else "evidence/screenshots/wireshark-dns.png"

    if not events:
        raise ValueError("tcpdump produced no supported packet summary lines")

    # Link DNS response observations to their matching query only when the
    # transaction ID and reversed endpoints identify a unique query.
    queries = [event for event in events if event["action"] == "dns_query"]
    for event in events:
        if event["action"] != "dns_response":
            continue
        attrs = event["attributes"]
        matches = [query for query in queries if
            query["attributes"].get("dns_transaction_id") == attrs.get("dns_transaction_id")
            and query["attributes"].get("source_ip") == attrs.get("destination_ip")
            and query["attributes"].get("destination_ip") == attrs.get("source_ip")
            and query["attributes"].get("source_port") == attrs.get("destination_port")
            and query["attributes"].get("destination_port") == attrs.get("source_port")]
        if len(matches) == 1:
            event["object_reference"] = matches[0]["object_reference"]
            attrs["paired_query_event_id"] = matches[0]["event_id"]

    return {
        "export_version": "1.0",
        "case_id": "WIRESHARK-PRACTICE-001",
        "source_capture": {
            "path": f"evidence/captures/{capture.name}",
            "filename": capture.name,
            "size_bytes": capture.stat().st_size,
            "sha256": digest,
            "frame_count": len(events),
        },
        "examination": {
            "tool": _tcpdump_version(executable),
            "commands": ["tcpdump -nn -tt -r <capture>", "tcpdump -nn -tt -A -r <capture>"],
            "timezone_note": "PCAP epoch timestamps are represented as UTC. No independent capture timezone metadata was available.",
            "scope_note": "This is a packet-summary export. TCP stream reconstruction and complete protocol reassembly are not performed by Chronicle.",
            "decoder_discrepancy": "The supplied Wireshark HTTP-filter screenshot shows HTTP on frames 4, 18, 27, and 38. tcpdump also labels HTTP in several adjacent TCP segments. Both summaries are preserved; Wireshark screenshot annotations are explicitly attributed to that exhibit.",
        },
        "events": events,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, default=DEFAULT_CAPTURE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = extract_observations(args.capture)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(result['events'])} observations to {args.output}")
    print(f"Capture SHA-256: {result['source_capture']['sha256']}")


if __name__ == "__main__":
    main()
