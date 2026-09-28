UV := uv run --frozen --offline --group dev
PY := $(UV) python

.PHONY: install format format-check lint typecheck unit integration coverage import-smoke workflow-check lock-check security dist-check audit all

install:
	uv sync --frozen --group dev

format:
	$(UV) ruff format src/ai_quant_trade tests scripts

format-check:
	$(UV) ruff format --check src/ai_quant_trade tests scripts

lint:
	$(UV) ruff check src/ai_quant_trade tests scripts

typecheck:
	$(UV) mypy

unit:
	$(UV) pytest tests/unit

integration:
	$(UV) pytest tests/integration

coverage:
	$(UV) pytest tests/unit tests/integration --cov=ai_quant_trade --cov-branch --cov-report=term-missing --cov-fail-under=90

import-smoke:
	$(PY) -c "import ai_quant_trade; print(ai_quant_trade.__version__)"
	$(UV) ai-quant-trade --help

workflow-check:
	$(PY) scripts/check_workflow.py

lock-check:
	uv lock --check --offline

security:
	$(PY) scripts/check_secrets.py
	$(PY) scripts/check_boundaries.py

dist-check:
	$(PY) scripts/check_dist.py

# Online vulnerability lookup is separate from the deterministic offline suite.
audit:
	@audit_file=$$(mktemp); trap 'rm -f "$$audit_file"' EXIT; \
	uv export --frozen --group dev --no-emit-project --format requirements-txt --output-file "$$audit_file" >/dev/null && \
	$(UV) pip-audit --requirement "$$audit_file" --disable-pip

all: format-check lint typecheck unit integration coverage import-smoke workflow-check lock-check security dist-check
