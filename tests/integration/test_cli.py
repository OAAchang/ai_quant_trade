"""Installed entrypoints work outside the repository's current directory."""

import subprocess
import sys
from pathlib import Path


def test_module_help_from_another_directory(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "ai_quant_trade", "--help"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "trading disabled" in result.stdout
    assert "order" not in result.stdout.lower()


def test_console_script_help_from_another_directory(tmp_path: Path) -> None:
    executable = Path(sys.executable).with_name("ai-quant-trade")
    result = subprocess.run(
        [str(executable), "--help"], cwd=tmp_path, check=False, capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "trading disabled" in result.stdout
