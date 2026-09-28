# ADR-0002: Python 3.11, uv and an isolated target-package quality gate

- Status: Accepted for Phase 01 implementation; independent review pending
- Date: 2026-09-28
- Owners: Personal fork maintainer
- Related Phase: 01

## Context

The upstream root requirements target an incompatible Python 3.8-era stack and CI only deploys documentation from `master`. Legacy examples include network and broker-facing paths; treating full-repository test discovery as the quality gate would be unsafe. `docs/PROJECT_CONTEXT.md` chooses Python 3.11 and uv for the new package.

## Decision

- Use CPython 3.11.14 and `uv 0.9.16` for the new `src/ai_quant_trade/` package. Commit `.python-version`, `pyproject.toml` and `uv.lock`; pin the Hatchling build backend exactly. Production runtime dependencies are empty in Phase 01.
- Keep the old `requirements.txt` and legacy examples as references only. The distribution includes only `src/ai_quant_trade/`, not the rest of `src/` or upstream directories.
- Scope pytest, Ruff, mypy, coverage and pre-commit to the new package, tests and scripts. Pytest has a socket-denial default; no CI test discovers provider/broker examples. CI performs an online dependency-vulnerability lookup separately from its offline tests.
- Use a local AST import check to enforce inward dependencies and prohibit relative imports; this is a minimum guard, not a proof against dynamic imports. Use a high-confidence credential-pattern scan that reports filenames only; this is not a full history/binary/entropy audit.
- Introduce only safe CLI help, typed configuration and structured logging. `TRADING_MODE` defaults to `disabled`; Phase 01 rejects `live` even when an explicit permission flag is supplied, and no submission path exists.

## Alternatives considered

- Extending the old root requirements/Black/Flake8 workflow was rejected because that stack failed to install and would force unrelated legacy changes.
- Installing all upstream examples into the target environment was rejected because of conflicting dependencies and network/broker side effects.
- Adding a settings or logging framework as a production dependency was rejected because the standard library covers this phase with a smaller attack/maintenance surface.
- Moving the whole repository into a single package was rejected by ADR-0001 and would make the migration unreviewable.

## Quant/data correctness impact

No data, price, timestamp, rule, fee or strategy semantics are implemented or migrated. Historical example results remain unvalidated, including the known momentum lookahead defect.

## Reliability/safety impact

Target-package tests deny sockets and the CLI has no trading command. This does not certify upstream examples, broker integration or live readiness. The logging formatter redacts common key/value secrets and GitHub-token patterns; callers must still avoid logging credentials and a later security phase must expand redaction and history scanning.

## Migration and rollback

Later phases add behavior behind these empty boundaries and extend lock/tests intentionally. Revert the Phase 01 package/config/CI/docs without touching upstream examples or Phase 00 governance; there is no data migration.

## Verification

Use `uv sync --frozen --group dev`, `make all`, `make audit`, a disposable-environment install and an outside-repository CLI/import smoke. Record exact results in `docs/status/PHASE_01.md`; a GitHub Actions run is additional evidence after PR publication.

## Consequences

The target package is deliberately featureless. CI package installation and vulnerability lookup still need trusted package/security services; test execution itself is offline. New dependencies require purpose, license, alternative and maintenance-risk review before changing the lock.
