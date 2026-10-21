import csv
from datetime import datetime, timezone
from pathlib import Path

from src.hashing import calculate_sha256


FIELDS = [
    "relative_path",
    "size_bytes",
    "sha256",
    "collected_at_utc",
]


def create_manifest(
    evidence_dir: str | Path,
    output_file: str | Path,
    additional_files: list[dict[str, str | Path]] | None = None,
) -> int:
    """Write a CSV inventory and SHA-256 manifest for evidence files."""
    root = Path(evidence_dir).resolve()
    output = Path(output_file).resolve()

    if not root.is_dir():
        raise FileNotFoundError(f"Evidence directory not found: {root}")

    output.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(
        path for path in root.rglob("*")
        if path.is_file() and path.resolve() != output
    )
    selected = [(path.relative_to(root).as_posix(), path) for path in files]
    existing = {path.resolve() for _, path in selected}
    for item in additional_files or []:
        path = Path(item["path"]).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Evidence file not found: {path}")
        if path == output or path in existing:
            continue
        selected.append((str(item["relative_path"]), path))
        existing.add(path)
    selected.sort(key=lambda entry: entry[0])

    with output.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDS)
        writer.writeheader()

        for relative_path, path in selected:
            writer.writerow({
                "relative_path": relative_path,
                "size_bytes": path.stat().st_size,
                "sha256": calculate_sha256(path),
                "collected_at_utc": datetime.now(timezone.utc).isoformat(),
            })

    return len(selected)
