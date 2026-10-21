"""Rebuild the fully synthetic Operation Glasshouse event fixture."""
import csv
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE_DIR = ROOT / "data" / "cases" / "operation-glasshouse"
EVALUATION_DIR = ROOT / "data" / "evaluation"
SEED = 1901
BASE = datetime(2026, 10, 17, 7, 0, tzinfo=timezone.utc)
FIELDS = [
    "event_id", "source_id", "timestamp", "source_type", "account_id",
    "host", "action", "object_reference", "source_reference", "bytes",
    "destination", "disposition",
]


def main() -> None:
    rng = random.Random(SEED)
    rows = []

    def add(source_id, minute, source_type, account, host, action, obj="", ref="", **extra):
        stamp = BASE + timedelta(minutes=minute, seconds=extra.pop("seconds", 0))
        rows.append({
            "source_id": source_id,
            "timestamp": stamp.isoformat().replace("+00:00", "Z"),
            "source_type": source_type,
            "account_id": account,
            "host": host,
            "action": action,
            "object_reference": obj,
            "source_reference": ref or f"{source_id}:{len(rows) + 1:04d}",
            "bytes": extra.pop("bytes", ""),
            "destination": extra.pop("destination", ""),
            "disposition": extra.pop("disposition", ""),
        })

    # A deliberately suspicious-looking sequence with a plausible authorized
    # maintenance explanation retained in the surrounding evidence.
    add("AUTH-01", 180, "authentication", "jlee", "WS-FIN-07", "login_failure", "vpn", "auth.log:0041")
    add("AUTH-01", 181, "authentication", "jlee", "WS-FIN-07", "login_failure", "vpn", "auth.log:0042")
    add("AUTH-01", 182, "authentication", "jlee", "WS-FIN-07", "login_failure", "vpn", "auth.log:0043")
    add("AUTH-01", 184, "authentication", "jlee", "WS-FIN-07", "login_success", "vpn", "auth.log:0044")
    add("ENDPOINT-01", 187, "file_activity", "jlee", "WS-FIN-07", "file_opened", "C:/Finance/Q4-forecast.xlsx", "endpoint.jsonl:0188")
    add("ENDPOINT-01", 190, "file_activity", "jlee", "WS-FIN-07", "file_copied", "C:/Finance/Q4-forecast.xlsx", "endpoint.jsonl:0191", disposition="to staging")
    add("ENDPOINT-01", 195, "file_activity", "jlee", "WS-FIN-07", "archive_created", "C:/Users/jlee/AppData/Local/Temp/q4-review.zip", "endpoint.jsonl:0196")
    add("NETWORK-01", 202, "network", "jlee", "WS-FIN-07", "network_upload", "q4-review.zip", "proxy.csv:0077", bytes=18432000, destination="198.51.100.24:443", disposition="new destination")

    # A competing benign explanation: a documented service account backup.
    add("AUTH-02", 360, "authentication", "svc-backup", "SRV-FS-02", "login_success", "scheduled task", "auth.log:0811")
    add("ENDPOINT-02", 364, "file_activity", "svc-backup", "SRV-FS-02", "archive_created", "D:/Backup/nightly-2026-10-17.zip", "endpoint.jsonl:0612", disposition="scheduled backup")
    add("NETWORK-02", 370, "network", "svc-backup", "SRV-FS-02", "network_upload", "nightly-2026-10-17.zip", "proxy.csv:0212", bytes=442368000, destination="203.0.113.18:443", disposition="approved backup endpoint")

    # Seeded background activity across three distinct source systems.
    accounts = ["jlee", "mrivera", "svc-backup", "analyst.kpatel", "build-agent"]
    hosts = ["WS-FIN-07", "WS-FIN-08", "SRV-FS-02", "WS-OPS-03", "BUILD-01"]
    auth_actions = ["login_success"] * 7 + ["login_failure", "mfa_challenge", "logout"]
    file_actions = ["file_opened", "file_modified", "file_created", "file_deleted"]
    for i in range(75):
        minute = rng.choice(list(range(15, 160)) + list(range(420, 900)))
        account, host = rng.choice(accounts), rng.choice(hosts)
        action = rng.choice(auth_actions)
        add("AUTH-01", minute, "authentication", account, host, action,
            rng.choice(["vpn", "sso", "finance-app"]), f"auth.log:bg-{i+1:03d}", seconds=rng.randrange(60))
    for i in range(78):
        minute = rng.choice(list(range(10, 160)) + list(range(420, 900)))
        account, host = rng.choice(accounts), rng.choice(hosts)
        obj = rng.choice(["C:/Finance/monthly.xlsx", "C:/Users/shared/readme.txt", "D:/Backup/index.db", "C:/Projects/build.log"])
        add("ENDPOINT-01" if i % 2 == 0 else "ENDPOINT-02", minute, "file_activity", account, host,
            rng.choice(file_actions), obj, f"endpoint.jsonl:bg-{i+1:03d}", seconds=rng.randrange(60))
    destinations = ["192.0.2.10:443", "203.0.113.18:443", "198.51.100.24:443", "10.20.0.12:445"]
    for i in range(76):
        minute = rng.choice(list(range(5, 160)) + list(range(420, 900)))
        account, host = rng.choice(accounts), rng.choice(hosts)
        add("NETWORK-01" if i % 2 == 0 else "NETWORK-02", minute, "network", account, host,
            rng.choice(["network_connection", "dns_query", "network_upload"]),
            rng.choice(["api.internal", "updates.vendor.test", "archive.zip", "telemetry"]),
            f"proxy.csv:bg-{i+1:03d}", seconds=rng.randrange(60),
            bytes=rng.choice([512, 2048, 32768, 1048576]), destination=rng.choice(destinations),
            disposition=rng.choice(["routine", "unknown", "approved service"]))

    rows.sort(key=lambda row: row["timestamp"])
    for index, row in enumerate(rows, 1):
        row["event_id"] = f"GH-E{index:04d}"

    CASE_DIR.mkdir(parents=True, exist_ok=True)
    with (CASE_DIR / "events.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    truth = {
        "case_id": "OPERATION-GLASSHOUSE",
        "label": "Synthetic evaluation metadata; never a Chronicle finding",
        "seed": SEED,
        "known_sequence_event_ids": [row["event_id"] for row in rows if row["source_reference"] in {
            "auth.log:0041", "auth.log:0042", "auth.log:0043", "auth.log:0044",
            "endpoint.jsonl:0196", "proxy.csv:0077",
        }],
        "benign_sequence_event_ids": [row["event_id"] for row in rows if row["source_reference"] in {
            "endpoint.jsonl:0612", "proxy.csv:0212",
        }],
        "notes": "The label describes generator intent for evaluation. It does not establish human identity, authorization, exfiltration, or a real incident.",
    }
    EVALUATION_DIR.mkdir(parents=True, exist_ok=True)
    (EVALUATION_DIR / "operation-glasshouse-ground-truth.json").write_text(
        json.dumps(truth, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
