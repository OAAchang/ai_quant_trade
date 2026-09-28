"""Fail on high-confidence credentials in text files without printing the values."""

import argparse
import re
import subprocess
from pathlib import Path

PATTERNS = (
    re.compile(b"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(b"\\b(?:AKIA|ASIA)[A-Z0-9]{16}\\b"),
    re.compile(b"\\bgh(?:p|o|u|s|r)_[A-Za-z0-9]{36}\\b"),
)


def tracked_and_untracked(root: Path) -> list[Path]:
    """List project files, including new untracked files before their first commit."""
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    return [root / name.decode("utf-8") for name in result.stdout.split(b"\0") if name]


def has_secret(path: Path) -> bool:
    """Inspect a file without exposing candidate contents in output."""
    if not path.is_file():
        return False
    data = path.read_bytes()
    if b"\0" in data:  # Binary assets need a separate artifact/history scanner.
        return False
    return any(pattern.search(data) is not None for pattern in PATTERNS)


def main() -> int:
    """Scan repository files or explicitly supplied paths."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, action="append", default=[])
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    paths = args.path or tracked_and_untracked(root)
    matches = [path for path in paths if has_secret(path)]
    for path in matches:
        print(f"Potential credential in: {path}")
    return 1 if matches else 0


if __name__ == "__main__":
    raise SystemExit(main())
