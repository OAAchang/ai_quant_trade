# PHASE_00 Status

## Status

COMPLETE for Phase 00 implementation and independent review — the first and second Reviews returned NO-GO, their documentation findings were corrected, and a third independent read-only Review returned GO with no unresolved current-phase P0/P1. Delivery remains pending the user's merge of PR #1 into the personal Fork's `Main`; Phase 01 has not started.

## Scope

Established the audit and governance baseline for fork `OAAchang/ai_quant_trade` at upstream snapshot `4e4cb796fab4fe59d7260a7654a6b902ef4d85a9`. Review remediation qualifies the repository and documentation entrypoints, clarifies gate policy, corrects the momentum-example lookahead audit, and inventories previously omitted test trees. No trading logic, data schema, runtime or example behavior was changed.

## Files changed

### Added

- `AGENTS.md`
- `PLANS.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/PROJECT_CHARTER.md`
- `docs/plans/PHASE_00_PLAN.md`
- `docs/audit/UPSTREAM_INVENTORY.md`
- `docs/audit/BASELINE_RESULTS.md`
- `docs/audit/REUSE_DECISIONS.md`
- `docs/audit/LICENSE_AND_PROVENANCE.md`
- `docs/architecture/CURRENT_STATE.md`
- `docs/architecture/TARGET_ARCHITECTURE.md`
- `docs/architecture/adr/0001-migration-strategy.md`
- `docs/acceptance/QUALITY_GATES.md`
- `docs/risks/RISK_REGISTER.md`
- `docs/status/PHASE_00.md`
- `docs/templates/ADR_TEMPLATE.md`
- `docs/templates/ACCEPTANCE_MATRIX_TEMPLATE.md`
- `docs/templates/PHASE_STATUS_TEMPLATE.md`

### Modified

- `.gitignore`: repository-local exception ensures required `AGENTS.md` is visible despite a host-global ignore rule.
- `README.md`, `README_EN.md`, `docs/index.md`: prominently qualify upstream historical claims and state that live use is not approved.
- `PLANS.md`, `docs/PROJECT_CHARTER.md`, `docs/acceptance/QUALITY_GATES.md`, `docs/risks/RISK_REGISTER.md`: distinguish current-phase blocking findings from isolated, owned future-phase risks without weakening the Phase 14 release gate.
- `docs/audit/LICENSE_AND_PROVENANCE.md`, `docs/status/PHASE_00.md`: record review-driven modifications, exact verification commands and finding disposition.
- `docs/audit/UPSTREAM_INVENTORY.md`, `docs/audit/BASELINE_RESULTS.md`, `docs/audit/REUSE_DECISIONS.md`, `docs/architecture/CURRENT_STATE.md`, `docs/plans/PHASE_00_PLAN.md`: correct the lookahead assessment and state the exact test-discovery boundary.
- `docs/risks/RISK_REGISTER.md`, `docs/acceptance/QUALITY_GATES.md`, `PLANS.md`: assign the future fix and offline-CI controls; retain the independent GO gate.
- Local `.git/config` (not a tracked file): added canonical `upstream` fetch URL and set its push URL to `no_push`.

### Deleted

- None.

## Decisions / ADRs

- ADR-0001 accepts incremental migration into a new **TARGET** `src/ai_quant_trade/` hexagonal core.
- The complete upstream tree remains unchanged as reference and rollback evidence.
- Existing runtime behavior is not copied merely because an example works; every migrated unit needs provenance and deterministic semantic tests.
- Research cannot control broker submission. Backtest, paper and eventual live paths must share domain, portfolio, risk, OMS and ledger semantics.
- All live capability remains disabled and broker-specific implementation is blocked pending official documents and authorized sandbox details.

## Commands run

| Command | Exit code | Result | Evidence |
|---|---:|---|---|
| `git status --short --branch`; branch/SHA/remote checks | 0 | Correct Phase branch; `HEAD` and base initially at audited SHA | Terminal output and baseline report |
| `git ls-remote --symref upstream HEAD` | 0 | Upstream `master` at audited SHA | `docs/audit/BASELINE_RESULTS.md` |
| File/language/size inventory commands | 0 | 1,110 files; major domains and large assets recorded | `docs/audit/UPSTREAM_INVENTORY.md` |
| `python3 --version`; `sw_vers` | 0 | Python 3.9.6; macOS 26.5.2 | Baseline report |
| Disposable venv `pip install -r requirements.txt` | 1 | Legacy NumPy/scikit-learn build failed under current Apple Clang | Baseline report |
| Host `python3 -m unittest discover -s unit_test -v` | 1 | Import failed: missing pandas | Baseline report |
| Disposable compatible test-dependency install + unittest discover | 0 | 8 tests passed in 21.000s using local fixtures | Baseline report |
| Redirected-cache `python3 -m compileall -q ...` | 0 | Selected Python sources compile | Baseline report |
| Isolated Flake8 4.0.1 on selected paths | 1 | 24 existing findings | Baseline report |
| High-confidence key/token pattern filename scan | 0 | No matching tracked non-notebook source file | Baseline report |
| Required-file and prompt-copy consistency checks | 0 after correcting ADR template metadata | Required files present; copied files match source pack | Final validation output |
| `git diff --check` | 0 | No whitespace errors in tracked diff | Final validation output |

### Reproducible follow-up checks (2026-09-28)

The original 2026-09-10 inventory/scan/path rows above are historical summaries, not reconstructed command transcripts. These commands were run during review remediation to make their scope and outcome reproducible:

| Exact command | Exit | Result |
|---|---:|---|
| `git ls-tree -r --name-only Main \| wc -l` | 0 | 1,110 files at the audited base commit |
| `git ls-tree -rz --name-only Main \| tr '\0' '\n' \| rg -c '\.py$'` (repeat with `md`, `png`, `ipynb`, `csv`) | 0 each | 180 Python, 557 Markdown, 240 PNG, 20 notebooks, 22 CSV; NUL-delimited paths avoid quoted-Unicode miscounts |
| `unzip -p /Users/lanbojini/Downloads/codex_quant_system_prompt_pack.zip codex_quant_system_prompt_pack/AGENTS.md \| cmp - AGENTS.md` | 0 | `AGENTS.md` matches the user-supplied pack byte-for-byte |
| `unzip -p /Users/lanbojini/Downloads/codex_quant_system_prompt_pack.zip codex_quant_system_prompt_pack/templates/ADR_TEMPLATE.md \| cmp - docs/templates/ADR_TEMPLATE.md` (repeat for `ACCEPTANCE_MATRIX_TEMPLATE.md` and `PHASE_STATUS_TEMPLATE.md`) | 0 each | Three templates match the pack; the project charter is now intentionally adapted and is recorded in the provenance ledger |
| `git ls-files --error-unmatch AGENTS.md PLANS.md docs/PROJECT_CONTEXT.md docs/PROJECT_CHARTER.md docs/plans/PHASE_00_PLAN.md docs/audit/UPSTREAM_INVENTORY.md docs/audit/BASELINE_RESULTS.md docs/audit/REUSE_DECISIONS.md docs/audit/LICENSE_AND_PROVENANCE.md docs/architecture/CURRENT_STATE.md docs/architecture/TARGET_ARCHITECTURE.md docs/architecture/adr/0001-migration-strategy.md docs/acceptance/QUALITY_GATES.md docs/risks/RISK_REGISTER.md docs/status/PHASE_00.md docs/templates/ADR_TEMPLATE.md docs/templates/ACCEPTANCE_MATRIX_TEMPLATE.md docs/templates/PHASE_STATUS_TEMPLATE.md` | 0 | All 18 required governance paths are tracked |
| `git grep -IlP -e '-----BEGIN (RSA \|EC \|OPENSSH )?PRIVATE KEY-----' -e '\b(AKIA\|ASIA)[0-9A-Z]{16}\b' -e '\b(ghp\|gho\|ghu\|ghs\|ghr)_[A-Za-z0-9]{36}\b' HEAD -- ':!*.ipynb'` | 1 | No match in tracked text outside notebooks; `-l` exposes filenames only; this is not a full secret audit |
| `git diff --check` | 0 | No whitespace errors in the uncommitted remediation diff |
| `rg -q '本 Fork 的安全状态（Phase 00）' README.md`; `rg -q 'Fork status \(Phase 00\)' README_EN.md`; `rg -q '安全状态（Phase 00）' docs/index.md` | 0 each | All three entrypoints expose the safety notice |
| `rg -n '从学习、模拟到实盘\|全流程覆盖\|支持 Python/C\+\+/CPU/GPU 等多种部署方式' README.md docs/index.md` | 1 | No remaining unqualified top-level capability phrase matching these historical claims |
| `rg -q 'current phase' docs/acceptance/QUALITY_GATES.md`; `rg -q 'Phase 14 cannot release with unresolved P0/P1 risks' docs/risks/RISK_REGISTER.md` | 0 each | Current-phase and release-gate distinctions are present |
| `PYTHONDONTWRITEBYTECODE=1 /tmp/phase00-review-env.Y5dk5n/venv/bin/python -B -m unittest discover -s unit_test -v` | 0 | 8/8 deterministic legacy example tests passed in the reviewer's temporary Python 3.11 environment |
| `PYTHONPYCACHEPREFIX=/tmp/phase00-review-pycache-remediation python3 -B -m compileall -q quant_brain egs_trade/vanilla/momentum_rotation unit_test` | 0 | Selected legacy Python sources compile; cache stays outside the repository |
| `/tmp/phase00-review-env.Y5dk5n/venv/bin/flake8 quant_brain egs_trade/vanilla/momentum_rotation unit_test --ignore=E501,F541,E266,E402,W503,E731,E203 --quiet` | 1 | Existing Flake8 failures remain in legacy code; no Python source was changed by this remediation |

The independent reviewer separately ran the eight local-fixture tests in a temporary Python 3.11 environment (8/8 passed), selected-source compilation (passed), Flake8 4.0.1 (24 legacy findings), and a default-Python test attempt (missing `pandas`). Its root-dependency dry run was interrupted; this does not supersede the original failed-install record.

### Second-review remediation checks (2026-09-28)

| Exact command | Exit | Result |
|---|---:|---|
| `rg -n '^\s*(async )?def test_' egs_aide/看盘神器/v2/tests \| wc -l` | 0 | 156 test functions in the desktop-helper tree; 11 `test_*.py` modules were enumerated |
| `rg -n '^\s*(async )?def test_' egs_skill/broker-research-analyst/tests \| wc -l` | 0 | Four test functions, including the Eastmoney network test; this command inspects source only |
| `PYTHONDONTWRITEBYTECODE=1 /tmp/phase00-review-env.Y5dk5n/venv/bin/python -B -m unittest discover -s unit_test -v` | 0 | 8/8 selected local-fixture tests passed; no broader test discovery was attempted |
| `PYTHONPYCACHEPREFIX=/tmp/phase00-review-pycache-remediation-2 python3 -B -m compileall -q quant_brain egs_trade/vanilla/momentum_rotation unit_test` | 0 | Selected Python sources compiled; cache outside repository |
| `/tmp/phase00-review-env.Y5dk5n/venv/bin/flake8 quant_brain egs_trade/vanilla/momentum_rotation unit_test --ignore=E501,F541,E266,E402,W503,E731,E203 --quiet` | 1 | Pre-existing lint findings in 11 legacy files; no Python source changed |

The second review identified that `_rebalance()` sizes current-open orders through `_mark_to_market(..., trade_date)` and `_position_value(..., trade_date)`, which reads the final close for `trade_date`. Its read-only mutation reproduction changed only that close while holding open prices and previous-day targets fixed, yet changed opening orders. This is a P1 no-lookahead defect in the existing example, not a passing feature. The Phase 00 response is to document, isolate and assign it to Phase 04; correcting runtime behavior is out of scope here.

### Third independent read-only Review (2026-09-28)

- Reviewer task: `01a0e767-887a-7e83-8ed5-3c568fd98652`; decision: **GO for Phase 00 only**, no new current-phase blocking finding. The reviewer reported P00-01 through P00-10 as PASS and made no file, commit, or PR changes.
- The reviewer independently reproduced the same-day-close leak: changing only the current day's final close from 10 to 11, with open price, initial holdings and previous-day targets fixed, changed AAA opening buy quantity from 500 to 400 shares. The existing eight tests remain insufficient to establish no-lookahead correctness; `R-BT-001` stays OPEN for Phase 04.
- The reviewer confirmed 11 desktop-helper test modules/156 test functions and four broker-research test functions, including the Eastmoney test not protected under pytest by `SKIP_NETWORK_TEST`. `R-TEST-002` stays OPEN for Phase 01.
- Its offline selected baseline ran 8/8 tests successfully, selected-source syntax checks passed, and Flake8 still reported 24 legacy findings. It also checked the 18 required governance paths, template provenance, whitespace, and local/remote tree equality. It did not run provider/broker paths, full-repository pytest or a new root dependency installation.

## Acceptance matrix

| Criterion | PASS/FAIL/BLOCKED | Evidence |
|---|---|---|
| Personal fork and upstream identity are recorded; upstream push fails closed | PASS | Git remotes and audited SHA |
| Major code/data/research/execution domains have a disposition | PASS | Upstream inventory and reuse decisions |
| Target architecture separates domain/application/ports/adapters/research/runtime | PASS | Target architecture and ADR-0001 |
| Migration is incremental, source-attributed and reversible | PASS | Plan, provenance policy and ADR rollback |
| Apache-2.0 obligations are retained and provenance gaps are explicit | PASS | License/provenance document; root `LICENSE` untouched |
| Existing install/tests/static checks have truthful results and an explicit discovery boundary | PASS locally | Baseline report includes PASS/FAIL outcomes; other test trees inventoried but not run |
| Required risks include lookahead, survivorship, fees, duplicate orders, ledger drift, secrets and broker uncertainty | PASS | Risk register |
| Required Phase 00 files exist and target-only paths are labeled | PASS | Final required-path validation |
| Repository and documentation entrypoints do not imply verified live readiness | PASS | Safety notices and qualified claims verified by third reviewer |
| No new strategy, backtest, factor, OMS or broker implementation | PASS | Git diff scope |
| Independent reviewer gives GO with no unresolved current-phase P0/P1 finding | PASS | Third independent read-only Review `01a0e767-887a-7e83-8ed5-3c568fd98652`: GO for Phase 00 only |

## Risks and limitations

- The root dependency manifest is not installable in the audited environment; the eight passing tests required a supplemental unpinned environment.
- Existing code has known fee/metric correctness defects and direct Wind order calls. It is not production-ready.
- The momentum example leaks same-day final close into opening order sizing. Its eight passing tests do not establish no-lookahead behavior; the example remains reference-only pending Phase 04 correction and mutation proof.
- Other test trees were not executed. Repository-wide pytest would collect a public Eastmoney network test; Phase 01 CI must scope offline tests explicitly.
- Data providers, historical/PIT coverage, broker, official API docs, sandbox, production operations and rule sources remain undecided.
- Third-party provenance for many notebooks, datasets, images, PDFs and snippets is incomplete.
- The prompt pack has recorded provenance but no included license file; public redistribution rights should be confirmed.
- Phase 00 did not run any provider, Wind or broker path and makes no claim about profitability or live readiness. GitHub branch creation and documentation delivery are repository writes, not trading-system writes.

## Review findings disposition

- `P1-01` — ACCEPT: added prominent warnings and qualified capability/return statements in the fork's Chinese/English README and MkDocs entrypoint; `P00-08` awaits independent re-review.
- `P1-02` — ACCEPT: clarified current-phase blocking findings, isolated deferred risks, owner/control requirements and the unconditional Phase 14 release gate across the roadmap, charter, quality gates and risk register.
- `P2-01` — ACCEPT: recorded exact follow-up inventory, copy-comparison, tracked-path, filename-only secret-scan and whitespace commands above. The original shell transcript is not claimed to have been reconstructed.
- `R2-P1-01` — ACCEPT: corrected the false no-lookahead claim in inventory/current-state/reuse documents and registered `R-BT-001` with Phase 04 owner, isolation rule and mutation-test gate. The existing strategy is intentionally unchanged in Phase 00.
- `R2-P2-01` — ACCEPT: inventoried both omitted test trees, stated that they were not run, and registered `R-TEST-002` so Phase 01 CI cannot silently discover the Eastmoney network test.
- `R3` — third independent read-only Review issued GO for Phase 00 after checking both remediation rounds and all ten acceptance items. The earlier two NO-GO decisions remain part of the audit trail; no legacy/future-phase risk is represented as fixed or live-ready.

## Out-of-scope confirmed

- No new trading logic, backtest engine, factor, OMS or broker adapter was implemented.
- No legacy directory was moved or deleted.
- No dependency version or legacy test was changed to make the baseline appear green.
- No provider or broker network write, credential use, account connection, paper order or real order occurred. Only authorized GitHub branch/document delivery writes were made.
- Phase 01 was not started.

## Next action

The user reviews and merges PR #1 into the personal Fork's `Main`. Do not begin Phase 01 until that merge; then re-check the merged branch and create the Phase 01 branch.
