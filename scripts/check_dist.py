"""Build and verify the isolated wheel and source distribution offline."""

import argparse
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SDIST_ROOT_FILES = {".gitignore", "LICENSE", "README.md", "pyproject.toml", "PKG-INFO"}
WHEEL_METADATA_FILES = {"METADATA", "WHEEL", "entry_points.txt", "licenses/LICENSE", "RECORD"}


def validate_sdist(path: Path) -> list[str]:
    """Reject any source archive member outside target package and build metadata."""
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
    errors: list[str] = []
    names: set[str] = set()
    for member in members:
        parts = PurePosixPath(member.name).parts
        if ".." in parts or len(parts) < 2 or not parts[0].startswith("ai_quant_trade-"):
            errors.append(f"unexpected sdist path: {member.name}")
            continue
        relative = "/".join(parts[1:])
        names.add(relative)
        if member.issym() or member.islnk() or not member.isfile():
            errors.append(f"unexpected sdist member type: {member.name}")
        if relative not in SDIST_ROOT_FILES and not (
            relative.startswith("src/ai_quant_trade/") and relative.endswith(".py")
        ):
            errors.append(f"unexpected sdist file: {relative}")
    for required in ("pyproject.toml", "LICENSE", "README.md", "src/ai_quant_trade/__init__.py"):
        if required not in names:
            errors.append(f"missing sdist file: {required}")
    return errors


def validate_wheel(path: Path) -> list[str]:
    """Reject wheel members outside the target package and wheel metadata."""
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
    errors: list[str] = []
    for name in names:
        parts = PurePosixPath(name).parts
        if ".." in parts or name.startswith("/"):
            errors.append(f"unsafe wheel path: {name}")
        elif name.startswith("ai_quant_trade/") and name.endswith(".py"):
            continue
        elif len(parts) >= 2 and parts[0].endswith(".dist-info"):
            if "/".join(parts[1:]) not in WHEEL_METADATA_FILES:
                errors.append(f"unexpected wheel metadata: {name}")
        else:
            errors.append(f"unexpected wheel file: {name}")
    if "ai_quant_trade/__init__.py" not in names:
        errors.append("missing wheel package init")
    return errors


def run(command: list[str], *, cwd: Path) -> None:
    """Run one safe local distribution check, failing on nonzero exit."""
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    """Check supplied artifacts or build, inspect and smoke-install fresh ones."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdist", type=Path)
    parser.add_argument("--wheel", type=Path)
    args = parser.parse_args()
    if bool(args.sdist) != bool(args.wheel):
        parser.error("--sdist and --wheel must be given together")
    if args.sdist and args.wheel:
        errors = validate_sdist(args.sdist) + validate_wheel(args.wheel)
    else:
        with tempfile.TemporaryDirectory(prefix="phase01-dist-") as temporary:
            root = Path(temporary)
            out = root / "dist"
            run(
                [
                    "uv",
                    "build",
                    "--wheel",
                    "--sdist",
                    "--offline",
                    "--quiet",
                    "--out-dir",
                    str(out),
                ],
                cwd=PROJECT_ROOT,
            )
            sdists = list(out.glob("*.tar.gz"))
            wheels = list(out.glob("*.whl"))
            if len(sdists) != 1 or len(wheels) != 1:
                print("expected exactly one sdist and one wheel")
                return 1
            errors = validate_sdist(sdists[0]) + validate_wheel(wheels[0])
            if errors:
                for error in errors:
                    print(error)
                return 1
            venv = root / "venv"
            run(["uv", "venv", "--offline", "--python", "3.11.14", str(venv)], cwd=root)
            python = venv / "bin/python"
            run(
                ["uv", "pip", "install", "--offline", "--python", str(python), str(sdists[0])],
                cwd=root,
            )
            run([str(python), "-c", "import ai_quant_trade"], cwd=root)
            run([str(venv / "bin/ai-quant-trade"), "--help"], cwd=root)
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
