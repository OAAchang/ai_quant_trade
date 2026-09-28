# Phase 01 target-package development setup

This is the installation path for the new `ai_quant_trade` package only. The upstream `requirements.txt`, examples and root-level tutorials are not part of the new distribution. Python 3.11.14 and uv 0.9.16 are the tested versions; `uv.lock` pins development packages, and Hatchling is pinned as the build backend in `pyproject.toml`.

```sh
uv python install 3.11.14
uv sync --frozen --group dev
make all
make audit
```

`uv sync` installs the package editable from `src/ai_quant_trade/`. The install and online `make audit` need a package index/vulnerability service; `make all` runs with `uv run --offline` and pytest denies sockets. CI never supplies broker credentials, uses no provider data, and does not discover old test directories. To test a fresh environment without touching the project `.venv`, set `UV_PROJECT_ENVIRONMENT` to a disposable directory and run the same frozen sync; then invoke that environment's `python` and `ai-quant-trade --help` from outside the repository. `uv lock --check --offline` confirms the committed lock agrees with the manifest.

| Command | Purpose |
|---|---|
| `make format` | Apply Ruff formatting to new package/tests/scripts only |
| `make format-check` | Non-mutating formatting gate |
| `make lint` | Ruff static checks on new paths |
| `make typecheck` | Strict mypy on new paths |
| `make unit` / `make integration` | Explicit offline test roots |
| `make coverage` | Both test roots with branch coverage, minimum 90% for the current tiny package |
| `make import-smoke` | Installed import and safe CLI help |
| `make workflow-check` | Parse CI YAML and assert required jobs/commands; not a full GitHub-runner simulation |
| `make lock-check` | Verify lock/manifest agreement offline |
| `make security` | High-confidence credential scan plus AST dependency check |
| `make dist-check` | Offline wheel/sdist build, archive whitelist validation, and sdist install/import/CLI smoke |
| `make audit` | Online vulnerability lookup for hashed locked development dependencies |
| `make all` | Deterministic offline gates above, excluding online audit |

The `pytest` default test path is `tests/`, and `--disable-socket` is enabled even when pytest is invoked directly. The network-denial plugin does not sandbox arbitrary subprocesses, so additions to integration tests must be reviewed for external calls. Do **not** run `pytest` over the full upstream tree as a CI shortcut: `egs_skill/broker-research-analyst/tests/test_adapter.py` contains an Eastmoney call not skipped under pytest. The distribution check accepts only target-package Python files and minimal build metadata; it does not package legacy examples, tests or the prompt pack.

## Dependency choices

There are **no production third-party runtime dependencies** in Phase 01. The development/build tools below are isolated to the build or dev group. Licenses for installed dev distributions were checked from package metadata on 2026-09-28; the lock fixes versions, but future updates require renewed review.

| Tool | Purpose | License | Alternative considered / maintenance risk |
|---|---|---|---|
| Hatchling | Build editable wheel | MIT | Setuptools; build backend is pinned to avoid unreviewed build drift |
| pytest, pytest-cov, pytest-socket | Behavior tests, coverage, socket denial | MIT | `unittest` and manual socket mocks; plugins need compatibility review on pytest upgrades |
| Ruff | Formatter and lint | MIT | Black + Flake8; one tool reduces configuration drift |
| mypy, types-PyYAML | Static types and YAML stubs for the workflow checker | MIT, Apache-2.0 | Pyright; stubs/tool can lag Python changes |
| pre-commit | Local repeatable hooks | MIT | Raw Git hooks; hooks require an initialized uv environment |
| PyYAML | Parse workflow YAML for syntax/structure | MIT | Hand-written parser; YAML parsing is not full Actions semantic validation |
| pip-audit | Audit locked development dependencies | Apache-2.0 | Dependabot/GitHub advisories; online database availability can fail independently of tests |

`make audit` initially found a known vulnerability in pytest 8.4.2. The constraint was raised to pytest 9.0.3 or later and the lock was regenerated; the subsequent locked audit found no known vulnerabilities. This is point-in-time evidence, not a guarantee against future advisories. The scanner deliberately reports file paths, not candidate secret values, and does not inspect Git history or binary assets.

The first independent Phase 01 Review found that the initial wheel was isolated but its source archive included old repository material. The sdist was restricted via Hatchling `only-include`, and `make dist-check` now inspects both artifacts and smoke-installs the sdist. The same review found gaps in domain import checks and JSON logging; these received negative tests. A follow-up independent Review is still required before GO.

## Safety boundary

`ai-quant-trade --help` is the only CLI behavior. `load_settings()` defaults to `disabled` and rejects an unknown mode. It rejects `live` without `TRADING_LIVE_ALLOWED=true`, and also rejects that explicit flag in Phase 01: no configuration can enable live behavior. There is **no** order, broker, cancellation or funds-transfer implementation. A later release gate will require whitelists, environment checks, manual approval, kill switch and audit logs. No package setting or test in this phase connects to a real account.
