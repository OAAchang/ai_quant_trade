"""Check inward-only imports in the target package without importing any code."""

import argparse
import ast
from pathlib import Path

LAYERS = {"domain", "ports", "application", "adapters", "research", "runtime", "cli"}
OUTER_ROOT_MODULES = {"settings", "logging"}
ALLOWED = {
    "domain": {"domain"},
    "ports": {"ports", "domain"},
    "application": {"application", "ports", "domain"},
    "adapters": {"adapters", "application", "ports", "domain"},
    "research": {"research", "application", "ports", "domain"},
    "runtime": {"runtime", "application", "ports", "domain", "adapters", "research"},
    "cli": LAYERS,
}
DOMAIN_FORBIDDEN = {
    "pandas",
    "numpy",
    "sqlalchemy",
    "duckdb",
    "requests",
    "httpx",
    "tushare",
    "WindPy",
    "socket",
    "sqlite3",
    "psycopg",
    "PyQt5",
}


def check_source(path: Path, package_root: Path) -> list[str]:
    """Return dependency violations for one target-package source file."""
    relative = path.relative_to(package_root)
    source_layer = relative.parts[0] if len(relative.parts) > 1 else None
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                violations.append(f"{path}:{node.lineno}: relative import bypasses layer policy")
                continue
            modules = [node.module] if node.module else []
            if node.module == "ai_quant_trade":
                modules.extend(f"ai_quant_trade.{alias.name}" for alias in node.names)
        else:
            continue
        for module in modules:
            if module is None:
                continue
            top = module.split(".", 1)[0]
            if source_layer == "domain" and top in DOMAIN_FORBIDDEN:
                violations.append(f"{path}:{node.lineno}: domain imports forbidden {module}")
            if not module.startswith("ai_quant_trade."):
                continue
            parts = module.split(".")
            if len(parts) < 2 or source_layer not in LAYERS:
                continue
            target_layer = parts[1]
            if target_layer in OUTER_ROOT_MODULES and source_layer not in {"runtime", "cli"}:
                violations.append(
                    f"{path}:{node.lineno}: {source_layer} imports outer {target_layer}"
                )
                continue
            if target_layer not in LAYERS:
                continue
            if target_layer not in ALLOWED[source_layer]:
                violations.append(
                    f"{path}:{node.lineno}: {source_layer} imports outward {target_layer}"
                )
    return violations


def check_tree(package_root: Path) -> list[str]:
    """Return all inward-dependency violations under a package root."""
    return [
        issue
        for path in sorted(package_root.rglob("*.py"))
        for issue in check_source(path, package_root)
    ]


def main() -> int:
    """Check the checked-out package or a supplied fixture root."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1] / "src/ai_quant_trade"
    )
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error(f"package root does not exist: {args.root}")
    issues = check_tree(args.root)
    for issue in issues:
        print(issue)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
