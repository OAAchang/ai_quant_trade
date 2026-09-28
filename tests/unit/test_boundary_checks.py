"""The source-tree import rule rejects an outward dependency."""

import subprocess
import sys
from pathlib import Path

import pytest


def test_outward_import_is_rejected(tmp_path: Path) -> None:
    package = tmp_path / "ai_quant_trade"
    domain = package / "domain"
    domain.mkdir(parents=True)
    (domain / "model.py").write_text("import ai_quant_trade.adapters\n", encoding="utf-8")
    script = Path(__file__).resolve().parents[2] / "scripts/check_boundaries.py"
    result = subprocess.run(
        [sys.executable, str(script), "--root", str(package)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "domain imports outward adapters" in result.stdout


def test_target_package_respects_boundaries() -> None:
    script = Path(__file__).resolve().parents[2] / "scripts/check_boundaries.py"
    result = subprocess.run(
        [sys.executable, str(script)], check=False, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout


def test_from_root_alias_cannot_bypass_policy(tmp_path: Path) -> None:
    package = tmp_path / "ai_quant_trade"
    domain = package / "domain"
    domain.mkdir(parents=True)
    (domain / "model.py").write_text(
        "from ai_quant_trade import adapters\nfrom ai_quant_trade import settings\n",
        encoding="utf-8",
    )
    script = Path(__file__).resolve().parents[2] / "scripts/check_boundaries.py"
    result = subprocess.run(
        [sys.executable, str(script), "--root", str(package)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "domain imports outward adapters" in result.stdout
    assert "domain imports outer settings" in result.stdout


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("import yaml\n", "domain imports forbidden yaml"),
        ("import urllib.request\n", "domain imports forbidden urllib.request"),
        ("from ai_quant_trade import __main__\n", "domain imports unclassified __main__"),
    ],
)
def test_domain_rejects_unclassified_or_io_import(
    tmp_path: Path, source: str, expected: str
) -> None:
    package = tmp_path / "ai_quant_trade"
    domain = package / "domain"
    domain.mkdir(parents=True)
    (domain / "probe.py").write_text(source, encoding="utf-8")
    script = Path(__file__).resolve().parents[2] / "scripts/check_boundaries.py"
    result = subprocess.run(
        [sys.executable, str(script), "--root", str(package)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert expected in result.stdout
