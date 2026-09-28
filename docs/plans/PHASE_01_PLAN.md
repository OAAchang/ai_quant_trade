# Phase 01 Plan — Foundation, Dependencies and Offline CI

## Current state

### Facts

- PR #1 was merged into the personal fork's `Main` as `fec52783f068b19f0d0f821aabcc9ba34b1bbaff`. The merged tree matches the Phase 00 reviewed tree. This branch, `phase-01-foundation-ci`, starts from `origin/Main` with a clean worktree.
- The repository has no root `pyproject.toml`, lock, importable target package, type-check configuration or code-test CI. `src/tools/` is unrelated legacy material and must not become the target package.
- Root `requirements.txt` is a Python 3.8-era legacy manifest that failed to install during Phase 00. The existing pre-commit Black hook targets nonexistent `qlib`. The only workflow deploys docs from `master`, not the fork's `Main`.
- Phase 00 ran eight local-fixture momentum tests, but they do not prove no-lookahead safety. Other test trees are outside that baseline; one `egs_skill/broker-research-analyst` test calls Eastmoney when collected by pytest. Full-repository pytest is unsafe as a default CI command.
- The host has `uv 0.9.16` and a managed CPython 3.11.14 interpreter; the host-default `python3` is 3.9.6.

### Assumptions

- Python 3.11 is the project interpreter for the new package. The new package can begin with no production third-party dependency; standard-library dataclasses, enum, argparse and logging are sufficient for Phase 01.
- The target package is named `ai_quant_trade` per `docs/PROJECT_CONTEXT.md`. The legacy tree remains reference-only and is not installed as part of the new distribution.
- Dependency installation may contact the package index; **tests and package runtime** must be offline and must never contact providers or brokers. Security checks must not need runtime secrets.

### Unknowns

- Data providers, trading rules and broker remain undecided; no placeholder implementation will guess their APIs.
- Public CI runner behavior cannot be observed until the branch is pushed. Local workflow syntax/structure and equivalent commands will be checked, but a GitHub run is separate evidence.

## Goals

1. Add a minimal editable-installable `src/ai_quant_trade/` package with empty hexagonal layers, typed settings, structured JSON logging and a safe CLI help entrypoint.
2. Lock Python 3.11 development dependencies and document an exact clean-install procedure.
3. Provide one documented command surface for format, lint, typecheck, unit, integration and all checks.
4. Add deterministic positive/negative tests for settings, CLI, logging, dependency direction and offline test isolation.
5. Add CI and pre-commit checks scoped to the new package/tests; detect obvious credential patterns and audit locked dependencies without running legacy provider/broker tests.

## Non-goals

- No strategy, backtest, provider, rule, ledger, OMS, paper or live adapter implementation.
- No migration or refactor of legacy examples/tests; no selection of production broker or data source.
- No attempt to make all legacy dependencies compatible with Python 3.11 or to certify historical examples as safe.

## Planned changes

1. Create `pyproject.toml`, `.python-version`, `uv.lock`, new package/layer `__init__.py` files, a minimal CLI, settings module and logging initializer.
2. Create scoped tests and fixtures; enforce default `disabled`, reject unknown mode and all live requests in Phase 01 (including requests with an explicit flag), and deny network sockets during the new test suite.
3. Define an import-boundary policy and executable AST check for target-package layer imports. No legacy package is imported by the new distribution.
4. Add `Makefile`, CI and pre-commit. CI installs from lock and runs format, lint, typecheck, scoped pytest/coverage, package/CLI smoke, workflow validation and security checks. Keep the existing docs workflow untouched in this phase unless it directly conflicts with the new CI.
5. Document setup, dependency rationale/license/alternatives, migration boundary and exact verification outcomes in `docs/development/SETUP.md`, `docs/architecture/DEPENDENCY_RULES.md` and `docs/status/PHASE_01.md`.

## Data and interface migration

- No data format, database schema, provider field, order schema or public trading interface changes.
- The new package exposes only a safe CLI and settings/logging APIs. No import or runtime path connects it to legacy broker/provider modules.
- `requirements.txt` remains as historical legacy input, not the authoritative target-package manifest. `pyproject.toml` and `uv.lock` govern only the new package.

## Risks and controls

| Risk | Control |
|---|---|
| Full-repo pytest executes Eastmoney network test | Scope discovery to `tests/`; deny sockets in test process; do not import legacy test trees |
| `live` accidentally enabled by environment/config | Default `disabled`; typed enum validation; reject live and explicit enable flags entirely in Phase 01; keep runtime submission absent |
| Supply-chain/network-dependent CI | Lock exact package versions; document install network requirement; run tests offline and prohibit provider/broker access; run credential/dependency checks separately |
| Replacing old pre-commit breaks legacy workflows | Scope new hooks to target package/tests/scripts; retain old code unchanged and document the boundary |
| Placeholder layers suggest unimplemented capability | Explain that skeleton names are boundaries only; CLI exposes no trading command |

## Test matrix and verification

| Check | Expected evidence |
|---|---|
| Clean CPython 3.11 lock install | Disposable environment, `uv sync --frozen` exit 0, editable import outside repo |
| Format and lint | Non-mutating Ruff checks on new files; exit 0 |
| Typecheck | mypy on target package and new tests; exit 0 |
| Unit/integration/coverage | pytest explicitly under `tests/unit` and `tests/integration`; network denied; coverage report and minimum threshold |
| Settings negatives | Missing/default, invalid mode and unauthorized live behavior |
| Dependency boundaries | AST import graph test rejects reversed layer imports and forbidden vendor imports in domain |
| CLI and logging smoke | Installed CLI `--help` exits 0; JSON log record has stable fields and no secret value |
| Workflow/security | YAML syntax/required-job validation, locked dependency audit or equivalent, secret-pattern scan; record exact commands and results |

## Rollback

Revert only the new Phase 01 package, lock, CI, command scripts, tests and docs in this branch. The Phase 00 governance baseline and all legacy examples remain intact; no database or data migration is needed.
