"""Validate CI YAML syntax and the minimum Phase 01 offline quality contract."""

import argparse
from pathlib import Path
from typing import Any

import yaml


def validate(path: Path) -> list[str]:
    """Return structural errors; this is not a replacement for GitHub's runner."""
    data: Any = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["workflow must be a mapping"]
    triggers = data.get("on")
    if not isinstance(triggers, dict) or "pull_request" not in triggers or "push" not in triggers:
        errors.append("workflow must run on push and pull_request")
    jobs = data.get("jobs")
    if not isinstance(jobs, dict) or "quality" not in jobs:
        return errors + ["quality job is missing"]
    quality = jobs["quality"]
    steps = quality.get("steps") if isinstance(quality, dict) else None
    if not isinstance(steps, list):
        return errors + ["quality steps are missing"]
    runs = [step.get("run", "") for step in steps if isinstance(step, dict)]
    combined = "\n".join(runs)
    for required in ("uv sync --frozen", "make all", "make audit"):
        if required not in combined:
            errors.append(f"required CI command missing: {required}")
    if "pytest ." in combined or "unittest discover" in combined:
        errors.append("CI must not discover legacy test trees")
    return errors


def main() -> int:
    """Validate the repository workflow or an explicit fixture file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--path",
        type=Path,
        default=Path(__file__).resolve().parents[1] / ".github/workflows/ci.yml",
    )
    args = parser.parse_args()
    try:
        errors = validate(args.path)
    except (OSError, yaml.YAMLError) as exc:
        print(f"workflow validation failed: {exc}")
        return 1
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
