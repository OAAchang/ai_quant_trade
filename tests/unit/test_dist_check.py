"""Distribution guard rejects a source archive that includes legacy code."""

import io
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path


def test_source_archive_rejects_legacy_member(tmp_path: Path) -> None:
    sdist = tmp_path / "ai_quant_trade-0.1.0.tar.gz"
    with tarfile.open(sdist, "w:gz") as archive:
        for relative in (
            "pyproject.toml",
            "LICENSE",
            "README.md",
            "src/ai_quant_trade/__init__.py",
            "egs_trade/legacy.py",
        ):
            data = b"fixture"
            info = tarfile.TarInfo(f"ai_quant_trade-0.1.0/{relative}")
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))
    wheel = tmp_path / "ai_quant_trade-0.1.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("ai_quant_trade/__init__.py", "")
    script = Path(__file__).resolve().parents[2] / "scripts/check_dist.py"
    result = subprocess.run(
        [sys.executable, str(script), "--sdist", str(sdist), "--wheel", str(wheel)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "unexpected sdist file: egs_trade/legacy.py" in result.stdout
