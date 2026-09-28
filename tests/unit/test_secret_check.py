"""The credential scan fails closed without printing candidate values."""

import subprocess
import sys
from pathlib import Path


def test_high_confidence_token_is_detected_without_disclosure(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate.txt"
    candidate.write_text("ghp_" + "A" * 36, encoding="utf-8")
    script = Path(__file__).resolve().parents[2] / "scripts/check_secrets.py"
    result = subprocess.run(
        [sys.executable, str(script), "--path", str(candidate)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert str(candidate) in result.stdout
    assert candidate.read_text(encoding="utf-8") not in result.stdout
