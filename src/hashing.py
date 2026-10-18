from hashlib import sha256
from pathlib import Path


def calculate_sha256(file_path: str | Path) -> str:
    """Return the SHA-256 hex digest of a file, reading it in chunks."""
    digest = sha256()

    with Path(file_path).open("rb") as evidence_file:
        for chunk in iter(lambda: evidence_file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def verify_sha256(file_path: str | Path, expected_hash: str) -> bool:
    """Check whether a file matches a previously recorded SHA-256 hash."""
    return calculate_sha256(file_path).lower() == expected_hash.strip().lower()
