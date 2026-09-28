# Phase 00 Plan — Audit and Governance Baseline

## Current state

### Facts

- The working repository is the personal fork `OAAchang/ai_quant_trade` on local branch `phase-00-audit-governance`, based on `Main` at commit `4e4cb796fab4fe59d7260a7654a6b902ef4d85a9`.
- `origin` points to the personal fork. The canonical upstream is `charliedream1/ai_quant_trade`; a local read-only-by-convention `upstream` remote still needs to be recorded.
- The repository is licensed under Apache-2.0 and contains 1,110 tracked files, including 180 Python files, 20 notebooks, 22 CSV files, and a large amount of documentation and media.
- The repository has no `pyproject.toml`, lock file, standard package build metadata, pytest configuration, type-check configuration, or code-test CI workflow.
- The root `requirements.txt` targets Python 3.8-era packages, while newer example-specific requirements target Python 3.12-era packages. The configured target is Python 3.11, but the current host default is Python 3.9.6.
- The selected baseline has one deterministic local-fixture module at `unit_test/test_momentum_rotation.py`; separate desktop-helper and broker-research test trees also exist and were not part of that baseline. Most core trading domains lack automated tests.
- `quant_brain` contains small backtest, fee, metric, portfolio, data-provider, and Wind integration modules. `egs_trade` contains strategy, Qlib, reinforcement-learning, and Wind paper-trading examples.
- The Wind paper-trading example calls account and order APIs directly and lacks the required OMS, idempotency, reconciliation, fail-closed live gateway, and persistent kill switch.
- No high-confidence private-key, AWS access-key, or GitHub token pattern was found in tracked non-notebook source files during the initial scan.

### Assumptions

- The future core will be a new `src/ai_quant_trade/` package rather than a relabeling of the existing examples.
- Existing code is reference material until a later phase proves its semantics with deterministic tests and records provenance.
- Phase 00 may add governance documents and local Git remote metadata, but will not alter trading behavior or move existing directories.

### Unknowns

- Primary, backup, and benchmark data providers.
- Broker selection, official API documentation, sandbox access, and account authorization.
- Authoritative effective-dated A-share trading-rule sources and the historical coverage required for V1.
- Production hosting, secret manager, alerting channel, database operations, recovery objectives, and release capital limits.
- Whether all third-party snippets, notebooks, data files, images, PDFs, and bundled artifacts have compatible redistribution terms.

## Goals

- Establish a factual inventory and baseline for the upstream snapshot.
- Classify major assets as direct reuse, migrate after validation, reference only, or deprecate.
- Record Apache-2.0 obligations and a provenance process for future copied or derived code.
- Define the target hexagonal architecture, incremental migration boundary, quality gates, and risk register.
- Run safe, reproducible baseline checks without accessing live accounts or submitting orders.
- Produce all Phase 00 required documents with evidence-linked PASS/FAIL/BLOCKED status.

## Non-goals

- No new strategy, factor, backtest engine, accounting engine, OMS, or broker adapter.
- No dependency modernization or production packaging; those belong to Phase 01.
- No large directory moves, deletion of legacy material, or cosmetic refactor.
- No public data-provider calls, Wind login, broker connection, credential use, or real/paper order submission.
- No claim that existing examples are production-ready or profitable.

## Planned changes

1. Record the canonical `upstream` Git remote and repository identity.
2. Make the required root `AGENTS.md` visible to repository-local Git status despite the host's global ignore rule.
3. Add `PLANS.md` as the phase roadmap and governance index.
4. Add upstream inventory, baseline results, reuse decisions, and license/provenance documents under `docs/audit/`.
5. Add current-state and target-architecture documents plus ADR 0001 under `docs/architecture/`.
6. Add measurable quality gates under `docs/acceptance/`.
7. Add a risk register under `docs/risks/`.
8. Add the Phase 00 status report under `docs/status/` after verification completes.

## Data and interface migration

- Phase 00 performs no data/schema/API migration.
- Existing files remain in place and retain their history and license notices.
- Future migration will copy the minimum validated behavior into `src/ai_quant_trade/`, with source path, source commit, license, semantic changes, tests, and rollback recorded for each migrated unit.
- Research, paper, and eventual live paths will converge on shared domain, portfolio, risk, OMS, and ledger semantics; examples will not call a broker from the new research layer.

## Risks

- Legacy examples may contain lookahead, survivorship bias, incorrect fees/metrics, or undocumented execution assumptions.
- Dependency conflicts and unavailable proprietary packages may prevent a full baseline installation.
- Large committed datasets/media increase clone and supply-chain review cost.
- Existing broker-facing examples could be mistaken for safe live-trading code.
- Third-party provenance may be incomplete even though the repository root is Apache-2.0.
- Global Git ignore rules could omit required governance files unless explicitly counteracted.

## Test matrix

| Check | Safety boundary | Expected evidence |
|---|---|---|
| Git identity, branch, remotes, commit | Read-only except adding local `upstream` remote | Exact URLs and commit SHA |
| Repository/package inventory | Read-only | Counts, paths, and domain classification |
| Root dependency installation in a disposable virtual environment | No project environment mutation; no credentials | Command, exit code, first blocking dependency |
| Existing deterministic unit tests | Local fixtures only; no public provider or broker | Test count and pass/fail/error output |
| Python syntax compilation | Cache redirected outside repository | Exit code and failing paths |
| Existing pre-commit/static checks | No auto-fix; report unavailable tools | Per-command outcome |
| High-confidence secret pattern scan | Do not print secret values | Matching filenames only |
| Required-document path validation | Local files only | Script output showing existing/target paths |
| Provenance completeness for planned copies | Governance documents only | Source/commit/license mapping table |

## Rollback

- Remove only the Phase 00-added governance documents and the repository-local ignore exception.
- Remove the local `upstream` remote if required.
- Do not alter or delete upstream code, datasets, history, `origin`, `Main`, or the existing `master` branch.
- Because Phase 00 contains no code/data migration, rollback does not require schema or runtime changes.
