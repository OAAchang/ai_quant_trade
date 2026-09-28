# Upstream Inventory

## Snapshot identity

| Item | Verified value |
|---|---|
| Personal fork | `https://github.com/OAAchang/ai_quant_trade` |
| Canonical upstream | `https://github.com/charliedream1/ai_quant_trade` |
| Upstream default branch | `master` |
| Audited commit | `4e4cb796fab4fe59d7260a7654a6b902ef4d85a9` |
| Commit date | `2026-09-06T22:56:54+08:00` |
| Root license | Apache License 2.0 (`LICENSE`) |
| Tracked files | 1,110 |
| Git pack size | 86.59 MiB |
| Major file counts | 180 Python, 557 Markdown, 240 PNG, 20 notebooks, 22 CSV |

The local `upstream` remote fetches from the canonical repository and has push URL `no_push` to fail closed on accidental pushes.

## Top-level asset inventory

| Path | Observed purpose | Evidence | Disposition |
|---|---|---|---|
| `quant_brain/` | Small legacy data, backtest, metric, portfolio, rule and RL modules | Python modules under `back_test/`, `data_io/`, `portfolio/`, `rules/`, `rl/` | REFERENCE ONLY; selected semantics may migrate after tests |
| `egs_trade/vanilla/momentum_rotation/` | Newer A-share momentum backtest with CSV/Tushare input and reports | Has dataclasses and prior-day selection, but open-order sizing reads same-day close; eight scoped fixture tests exist | MIGRATE AFTER VALIDATION |
| `egs_trade/vanilla/double_ma/` | Legacy vector/dataframe double-MA backtest | Calls `quant_brain` account, fee and metric helpers | REFERENCE ONLY |
| `egs_trade/ms_qlib/` | Qlib installation, data and strategy tutorials | Markdown, notebook and one data script; separate `pyqlib` requirement | REFERENCE ONLY until Phase 09 |
| `egs_trade/rl/` | Stable-Baselines/FinRL tutorials and bundled datasets | Old pinned Gym/Torch stack, notebooks, CSV data | REFERENCE ONLY |
| `egs_trade/paper_trade/wind/` | Wind WTTS simulation-account scripts | Direct `WindPy.w.torder`, `tquery`, `tcancel`, and login calls | DEPRECATE as an execution path; retain as reference |
| `egs_data/` | Examples for A-share, fund, futures, crypto, news and macro providers | Per-example requirements; many public network APIs | REFERENCE ONLY; adapter candidates require contracts and PIT review |
| `egs_alpha/` | Factor/alpha learning examples and external library notes | Example-oriented content without a common experiment contract | REFERENCE ONLY until Phase 07 |
| `egs_online_platform/` | JoinQuant/Uqer examples | Platform-specific notebooks and scripts | REFERENCE ONLY |
| `egs_aide/` | Desktop/watch-market helper applications | Excel/UI/video assets and separate dependencies | OUT OF V1 CORE; REFERENCE ONLY |
| `egs_fin_nlp/`, `egs_llm/` | NLP and LLM training/application examples | Heavy independent dependency stacks | OUT OF V1 CORE; REFERENCE ONLY |
| `egs_courses/`, `ai_notes/`, `a_全网优秀资源/` | Courses, notes and external-resource catalog | Documentation-heavy learning material | DIRECT REUSE as learning/reference content only |
| `egs_skill/` | A broker research helper skill and examples | Own requirements and `.env.example` | REFERENCE ONLY; security/provenance review required |
| `egs_aide/看盘神器/v2/tests/` | Desktop watch-market helper tests | 11 test modules and 156 `test_*` functions, outside the selected momentum baseline | REFERENCE ONLY; test isolation/dependency audit in Phase 01 |
| `egs_skill/broker-research-analyst/tests/` | Broker research helper tests | Four `test_*` functions; one calls the public Eastmoney endpoint during pytest collection/execution | REFERENCE ONLY; never include its network test in default CI |
| `tools/`, `src/tools/` | Logging, file, date, plotting and NLP utilities | Two overlapping tool trees; hidden cwd/global assumptions | MIGRATE AFTER VALIDATION or DEPRECATE duplicates |
| `unit_test/` | Tests and local fixtures | One `unittest` module with eight tests | DIRECT REUSE as baseline evidence; expand later |
| `runtime/` | Placeholder documentation | `README.md` contains only “系统部署使用” | DEPRECATE placeholder; target runtime is separate |
| `backup/` | Archived material | No production ownership boundary | DEPRECATE from active architecture; do not delete in Phase 00 |
| `docs/` | Environment, FAQ, project marketing and deployment documentation | MkDocs source plus Phase 00 governance additions | DIRECT REUSE where factual; separate governance from tutorials |
| `.github/workflows/docs-pages.yml` | MkDocs Pages build/deploy | Triggers only on `master`; no code quality tests | MIGRATE AFTER VALIDATION in Phase 01 |
| `requirements.txt` | Legacy repository-wide dependencies | Python `~=3.8.0`, pandas `~=1.2.4`, sklearn `~=0.24.1` | DEPRECATE as authoritative manifest in Phase 01 |
| `.pre-commit-config.yaml` | Black/Flake8 hooks | Old revisions; Black args include nonexistent root path `qlib` | MIGRATE AFTER VALIDATION in Phase 01 |
| `LICENSE` and existing history | Apache-2.0 license and upstream provenance | Root license and intact Git history | DIRECT REUSE; must be retained |

## Data domain

### Observed providers and stores

- Tushare wrappers exist in `quant_brain/data_io/api_tushare_data.py` and the momentum example.
- Wind data/account code exists under `quant_brain/data_io/wind/`.
- BaoStock and numerous provider demos exist under `egs_data/`.
- The momentum example writes downloaded results to mutable CSV files and reuses them based on file existence.
- Large historical CSV fixtures are committed for reinforcement-learning tutorials.

### Gaps against target

- No raw/normalized/curated immutable layering or dataset version manifest.
- No common `as_of` query contract, announcement-time financial model, revision history, or historical constituent service.
- `select_tushare_universe()` queries only `list_status="L"`, creating a survivorship-bias risk for historical studies.
- No cross-provider validation, schema version, corporate-action ledger, or distinction between research-adjusted and executable prices.

## Backtest, metrics, and strategy domain

- The legacy double-MA path uses mutable pandas state, floating-point cash, string order types, static rule parameters, and no event ledger.
- `quant_brain/back_test/cal_fee.py` computes commission rate times share count rather than transaction value and uses nondeterministic random slippage when configured.
- `quant_brain/back_test/risk_indicator.py` assigns benchmark covariance to both beta numerator and denominator, making beta invalid; several other metrics are marked TODO/FIXME.
- The momentum example selects targets from a previous available date, but its current-open rebalance sizing is **not** point-in-time safe: `_rebalance()` calls `_mark_to_market(..., trade_date)` and `_position_value(..., trade_date)`, which read `self.close.at[trade_date, code]`, the final close unavailable at that open. Changing only that day's close can change that day's opening orders even when opening prices and previous-day targets are fixed. Do not migrate this sizing logic without a no-lookahead mutation test and correction in Phase 04. It also lacks exchange calendars, T+1 lots, suspensions, price limits, dated fees, liquidity fills, immutable events, and Decimal accounting.
- Parameter selection sorts by test-period CAGR, so the current report flow is not a frozen out-of-sample evaluation process.
- No standardized factor lab, IC/RankIC/ICIR pipeline, no-lookahead mutation suite, or run manifest exists.

## Paper/live and reliability domain

- Wind examples log into a simulation account and call order, query, cancel and logout APIs directly.
- No broker-agnostic port, OMS state machine, idempotency key, append-only event store, inbox/outbox, crash recovery, reconciliation incident workflow, external persistent kill switch, or manual approval gate exists.
- The presence of Wind scripts is not evidence of production readiness. These paths must not be executed during CI or Phase 00.

## Testing and delivery domain

- The selected Phase 00 baseline ran only `unit_test/test_momentum_rotation.py`: eight deterministic tests using local CSV fixtures and temporary output directories. These tests do not detect the same-day-close sizing leak above.
- Two other test domains were inventoried but not executed in Phase 00: `egs_aide/看盘神器/v2/tests/` (11 modules, 156 `test_*` functions) and `egs_skill/broker-research-analyst/tests/test_adapter.py` (four functions). In the latter, `test_fetch_stock_reports()` directly contacts Eastmoney; its `SKIP_NETWORK_TEST` guard exists only under `if __name__ == "__main__"`, so it does not protect pytest collection. Phase 01 must explicitly scope offline CI test roots or add a genuine test-level network guard before broader discovery; do not run full-repository pytest by default.
- No tests were found for legacy fee calculation, beta/alpha, cash/position conservation, broker calls, replay/recovery, or adapter contracts.
- The sole GitHub Actions workflow builds and deploys documentation from `master`; it does not run tests, lint, type checking, secret scanning, or dependency auditing and is stale relative to default branch `Main`.
- No installable package metadata, lock file, typed settings, migrations, SBOM, deployment definition, or structured observability stack exists.

## Size and repository hygiene

- The two largest tracked files are RL tutorial CSVs of roughly 25.8 MiB and 23.1 MiB.
- An 8 MiB demonstration video, tokenizer data, duplicate GIFs, PDFs and many images materially increase clone size.
- Phase 00 does not delete or rewrite history. Later governance may move large derived artifacts to releases/object storage after provenance and reproducibility review.
