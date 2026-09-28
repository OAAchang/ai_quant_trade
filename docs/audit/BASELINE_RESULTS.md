# Baseline Results

## Environment

| Item | Observed result |
|---|---|
| Date/timezone | 2026-09-10, Asia/Shanghai |
| Host OS | macOS 26.5.2 (build 25F84) |
| Default Python | 3.9.6 |
| Target Python | 3.11 (configured, not installed on host) |
| `uv` | Not installed |
| Docker | Not installed |
| pytest / pre-commit / flake8 / pylint | Not installed globally |

All installation attempts used disposable `mktemp` virtual environments outside the repository. No provider, Wind, broker, credential, or order endpoint was contacted.

## Repository identity baseline

| Check | Exit | Result |
|---|---:|---|
| `git status --short --branch` | 0 | On `phase-00-audit-governance`; Phase 00 docs are the only working-tree changes |
| `git rev-parse Main` and `git rev-parse HEAD` | 0 | Both initially resolved to `4e4cb796fab4fe59d7260a7654a6b902ef4d85a9` |
| `git remote -v` | 0 | `origin` is the personal fork; `upstream` fetches canonical repo and push is `no_push` |
| `git ls-remote --symref upstream HEAD` | 0 | Upstream HEAD is `refs/heads/master` at the audited commit |

This verifies the previously completed clone/fork state; Phase 00 did not push or write to either GitHub repository.

## Dependency installation baseline

Command shape:

```text
python3 -m venv <temporary>/venv
<temporary>/venv/bin/python -m pip install -r requirements.txt
```

- Exit code: `1`.
- pip: 21.2.4 on Python 3.9.
- Resolution selected pandas 1.2.5 and scikit-learn 0.24.x source distributions.
- The scikit-learn build environment pinned NumPy 1.19.3, whose universal2 build failed under the current Apple Clang because `-faltivec` is unsupported.
- A subsequent fallback candidate began another source-build cycle and was stopped; no project files or project environment were changed.

Conclusion: the root dependency manifest is not reproducibly installable on the audited host and cannot be accepted as the Phase 01 target manifest.

## Existing test baseline

### Host environment

```text
python3 -m unittest discover -s unit_test -v
```

- Exit code: `1`.
- Result: discovery found the test module but import failed because `pandas` was not installed.
- Tests run: 1 loader error; 0 behavioral tests.

### Supplemental isolated test harness

To distinguish a broken root manifest from test behavior, a second disposable venv installed only the dependencies imported by the test path: unpinned compatible `pandas`, `PyYAML`, `matplotlib`, and `tushare`.

```text
<temporary>/venv/bin/python -m unittest discover -s unit_test -v
```

- Exit code: `0`.
- Result: 8 tests passed in 21.000 seconds.
- Data boundary: repository-local fixtures only; no Tushare token and no provider/broker call.
- Warnings: Matplotlib emitted PyParsing deprecation warnings.

This is useful positive evidence for the momentum example only. It does not validate the root dependency file, legacy core, A-share execution semantics, or live safety.

## Syntax baseline

```text
PYTHONPYCACHEPREFIX=<temporary>/pycache python3 -m compileall -q \
  quant_brain egs_trade/vanilla/momentum_rotation unit_test
```

- Exit code: `0`.
- Result: selected core/example/test Python sources compiled successfully; cache output was redirected outside the repository.

## Static analysis baseline

An isolated Flake8 4.0.1 run used the existing ignore list and did not modify files:

```text
flake8 quant_brain egs_trade/vanilla/momentum_rotation unit_test \
  --ignore=E501,F541,E266,E402,W503,E731,E203
```

- Exit code: `1`.
- Findings: 24.
- Main categories: unused imports/variables, trailing whitespace, over-indentation, and arithmetic-spacing violations.
- Existing pre-commit was not run because it can autoformat and its Black hook passes the nonexistent root path `qlib`; silently changing baseline code is outside Phase 00.
- Type checking and coverage: not configured, therefore not runnable.

## Secret and credential baseline

- A high-confidence scan for private-key blocks, AWS access-key IDs, and GitHub token formats returned no matching tracked non-notebook source file.
- Provider examples contain empty placeholders and environment-variable reads for API tokens.
- `egs_skill/broker-research-analyst/.env.example` exists and requires review before any real value is introduced.
- This is not a complete secret audit: notebooks, binary files, Git history, entropy scanning, and provider-specific formats require a dedicated scanner in Phase 01.

## Baseline verdict

| Area | State | Reason |
|---|---|---|
| Clone/fork identity | PASS | Fork, upstream, branches and commit independently verified |
| Root dependency install | FAIL | Legacy scientific stack does not build on audited host |
| Existing fixture tests | CONDITIONAL PASS | 8/8 pass only in a supplemental unpinned environment |
| Selected syntax | PASS | Compile check succeeded |
| Static checks | FAIL | 24 Flake8 findings; pre-commit config is stale |
| Type checks | NOT CONFIGURED | No tool/configuration |
| Code-test CI | NOT CONFIGURED | Docs deployment only |
| Live safety | NOT ACCEPTABLE | Direct Wind calls exist without target safety architecture |

Phase 00 records these failures without altering legacy code. Making the engineering baseline installable and enforceable belongs to Phase 01.
