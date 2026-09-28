"""Command-line help only; Phase 01 intentionally has no trading command."""

import argparse
from collections.abc import Sequence

from ai_quant_trade import __version__


def main(argv: Sequence[str] | None = None) -> int:
    """Display the safe foundation CLI and return a process exit code."""
    parser = argparse.ArgumentParser(
        prog="ai-quant-trade",
        description="A-share research platform foundation (trading disabled).",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.parse_args(argv)
    if not argv:
        parser.print_help()
    return 0
