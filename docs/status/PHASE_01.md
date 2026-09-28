# Phase 01 status — foundation, dependencies and CI

- Date: 2026-09-28
- Branch: `phase-01-foundation-ci`, based on the user-merged Phase 00 `origin/Main` tree (`fec52783f068b19f0d0f821aabcc9ba34b1bbaff`)
- Implementation: COMPLETE; first independent Review NO-GO findings F-01–F-04 repaired, follow-up independent Review GO, updated hosted CI successful; user merge pending
- Pull request: open and ready for user review [#2](https://github.com/OAAchang/ai_quant_trade/pull/2) against the personal Fork's `Main`; no automatic merge
- Trading state: `disabled` by default; Phase 01 rejects `live` even with an explicit enable flag; no order, broker, transfer, strategy or backtest implementation

## Completed scope

- Added an editable-installable `src/ai_quant_trade/` wheel package with empty domain/application/ports/adapters/research/runtime boundaries. The only CLI actions are help and version. Typed settings and JSON logging have behavior tests.
- Pinned CPython 3.11.14, the Hatchling build backend and a uv development lock. The target package has zero production third-party dependencies; old `requirements.txt` and example trees remain reference-only.
- Added scoped pytest/socket denial, branch coverage, Ruff, strict mypy, pre-commit hooks, structural GitHub Actions validation, import-boundary and high-confidence secret-pattern checks, offline wheel/sdist inspection and sdist-install smoke, and an online locked-dependency vulnerability audit.
- Added ADR-0002, dependency rules, setup instructions and accurate Fork-specific safety notices. No upstream example, data or trading path was migrated or rewritten.

## Changed files

- Added: `.python-version`, `pyproject.toml`, `uv.lock`, `Makefile`, `.github/workflows/ci.yml`, `src/ai_quant_trade/**`, `tests/**`, `scripts/check_{boundaries,dist,secrets,workflow}.py`, `docs/plans/PHASE_01_PLAN.md`, `docs/architecture/adr/0002-python-foundation.md`, `docs/architecture/DEPENDENCY_RULES.md`, `docs/development/SETUP.md`, this report.
- Modified: `.gitignore`, `.pre-commit-config.yaml`, `PLANS.md`, `README.md`, `README_EN.md`, `docs/index.md`, `docs/acceptance/QUALITY_GATES.md`.
- Deleted: none.

## Verification actually run

All commands below were run from the project root on macOS with CPython 3.11.14 and uv 0.9.16 unless noted. Exit codes are process exit codes, not forecasts of a hosted run.

| Command | Exit | Result / scope |
|---|---:|---|
| `uv lock` | 0 | Generated 51-package development lock after updating pytest constraint. |
| `uv sync --frozen --group dev --quiet` | 0 | Installed the target package and locked dev group. |
| `uv build --wheel --quiet` | 0 | Built the target wheel after a transient package-index retry. |
| `uv build --wheel --offline --quiet` | 0 | Rebuilt the target wheel with cached, pinned build backend and no network. |
| `UV_PROJECT_ENVIRONMENT="$phase01_clean_dir/venv" uv sync --frozen --offline --group dev --quiet` | 0 | Fresh disposable environment using the populated uv cache; no old project `.venv` required. |
| `cd "$phase01_clean_dir"; "$phase01_clean_dir/venv/bin/python" -c 'import ai_quant_trade; print(ai_quant_trade.__file__)'` | 0 | Imported editable package outside the repository working directory. |
| `"$phase01_clean_dir/venv/bin/ai-quant-trade" --help` from outside repo | 0 | Only safe help/version options displayed. |
| `make format` | 0 | Ruff formatted target package/tests/scripts. |
| Initial committed `make all` | 0 | 21 files checked; unit 20/20, integration 2/2, combined 22/22; branch coverage 93.67%. This did **not** detect the first Review's F-01–F-04. |
| Repair `make all` | 0 | 23 files format-checked; Ruff passed; mypy checked 23 files; unit 29/29, integration 2/2, combined 31/31; branch coverage 94.57%; import/help, workflow structure, lock agreement, security and new offline distribution build/inspect/install checks passed. |
| `make audit` | 0 | Locked development dependencies: no known vulnerabilities found at check time. |
| `git diff --cached --check` | 0 | No whitespace errors in the complete staged Phase 01 diff. |
| `uv run --frozen --offline --group dev pre-commit run --all-files` | 0 | All four scoped local hooks passed on staged files. |

The deliberate socket-denial test emits one expected `pytest-socket` warning when it attempts a blocked socket. It did not access the network. The CI YAML checker parses and checks required commands; it does **not** simulate all GitHub Actions semantics. Hosted GitHub Actions runs [36427212478](https://github.com/OAAchang/ai_quant_trade/actions/runs/36427212478) for repaired code head `5bcf7b9` and [36428009939](https://github.com/OAAchang/ai_quant_trade/actions/runs/36428009939) after the Review/CI evidence update both completed successfully on Linux, including lock installation, 31 tests, 94.57% branch coverage, offline sdist build/install and the online dependency audit. The earlier head `826270c2` also had a successful run, but that run preceded review repairs and is not the acceptance evidence.

### Failures found and repaired during implementation

- The first `make all` exited 1 on a Ruff `UP022` warning in the secret checker. The script was corrected; the final `make all` exited 0.
- The first audit invocation used `pip-audit --disable-pip` without a requirements input and exited 2. The command was corrected to audit a uv-exported locked requirements file.
- Audit of the initial lock exited 1 because pytest 8.4.2 was reported under `PYSEC-2026-1845`. The pytest constraint was raised to `>=9.0.3,<10`, the lock regenerated, and the final audit exited 0. This is a point-in-time finding, not a claim that future advisories are impossible.
- The first independent Review of `d690791` returned NO-GO (F-01 P1; F-02–F-04 P2). It demonstrated that an initial `uv build --sdist --offline` exited 0 yet created an 81 MB archive of 1,160 files including old broker material. Hatchling `only-include` now reduces the source archive to about 18 KB and 17 files; `make dist-check` checks both archive member sets and installs from the sdist outside the repository. Domain import rules and logging redaction/exception preservation received explicit negative tests. The fixes were subsequently re-reviewed and run by hosted CI.
- The independent follow-up Review of local commit `c88880c` versus `origin/Main` returned **GO** with F-01–F-04 **CLOSED** and no new current-stage P0/P1 or reportable P2/P3. It independently reran `make all`, `make audit`, pre-commit, clean install, wheel/sdist content and isolated sdist install checks, and checked the hosted CI logs. Its reviewed local Git tree `bf4f22d7` matched the draft PR #2 head tree. Review task: `01a0e814-df8e-7ab1-9c4e-766ec9d2daf5`.

## Phase 01 acceptance matrix

| Criterion | Status | Evidence |
|---|---|---|
| Editable, clean, locked Python 3.11 install independent of old `sys.path` | PASS locally | Disposable-env frozen/offline sync and import outside repository |
| Empty layer skeleton and explicit dependency direction | PASS locally | `src/ai_quant_trade/`, ADR-0002, dependency rules, AST negative tests |
| Documented single command surface | PASS locally | `Makefile`, setup guide and final `make all` |
| Scoped offline tests, no real broker/provider calls | PASS locally | pytest paths, default socket denial, negative socket test, no broker adapter code |
| Settings default disabled; invalid and live requests fail closed | PASS locally | Unit tests include unauthorized and explicitly flagged live requests |
| Format, lint, typecheck, pytest, coverage and package/CLI smoke | PASS locally | Repair `make all`, 31 tests and 94.57% branch coverage |
| Source and wheel distributions exclude historical code | PASS | `make dist-check`; independent Review verified 17-file sdist and wheel, isolated install |
| Secret scan and locked dependency audit | PASS locally | `make security` within `make all`; final `make audit` |
| GitHub Actions workflow syntax/structure and local reproducibility | PASS | `make workflow-check`, local `make all`/`make audit`, repaired-head hosted run 36427212478 success |
| Independent no-P0/P1 review | PASS | First Review NO-GO; follow-up Review GO closed F-01–F-04, no current P0/P1 |

## Risks, limits and next actions

- The current secret scan matches high-confidence patterns in tracked/untracked text; it does not scan Git history, binary blobs or arbitrary entropy. The dependency audit depends on a current external vulnerability service. A future phase must expand supply-chain controls and produce an SBOM before any production release.
- The AST boundary check does not prove absence of dynamic imports or arbitrary side effects. Code review remains necessary. The wheel, sdist and CI deliberately exclude old upstream examples; their defects and incompatible dependencies remain historical risks, not Phase 01 passes. Logging redaction supports specified common formats, not arbitrary secrets.
- Local pytest socket denial does not sandbox arbitrary subprocesses. The only subprocess-based integration checks invoke the installed CLI help/version, and there is no provider/broker implementation. New subprocess tests require review.
- Phase 01 independent GO is achieved, but this does **not** authorize Phase 02 or live trading. PR #2 awaits the user's review and merge into the personal Fork's `Main`; verify the actual merged Main tree before starting Phase 02. No PR was auto-merged.
