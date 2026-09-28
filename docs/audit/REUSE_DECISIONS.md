# Reuse Decisions

## Decision rules

- **DIRECT REUSE**: non-runtime asset with clear source, compatible purpose, and no unresolved semantic safety dependency.
- **MIGRATE AFTER VALIDATION**: potentially useful behavior that needs specification, deterministic tests, provenance and target-boundary adaptation before entering the new core.
- **REFERENCE ONLY**: educational or vendor-specific material that may inform design but must not be imported by the target core.
- **DEPRECATE**: obsolete, duplicated, unsafe-as-an-authoritative-path, or outside V1. It remains in place during Phase 00.

## Decisions

| Asset | Decision | Minimum evidence before change |
|---|---|---|
| Root `LICENSE`, Git history, original copyright headers | DIRECT REUSE | Retain unchanged and include in distributions |
| Project charter/context/governance templates | DIRECT REUSE for project governance | Track source and modifications |
| Local momentum CSV fixtures and eight tests | DIRECT REUSE as narrow baseline tests, not proof of no-lookahead safety | Pin compatible test environment in Phase 01; add future-close mutation coverage in Phase 04 |
| General learning documentation and resource indexes | DIRECT REUSE as reference content | Fix only factual/path drift when encountered |
| Momentum prior-day target selection / next-open scheduling | MIGRATE AFTER VALIDATION; do not copy current-open sizing | Fix same-day-close sizing leak, prove order invariance under future-close mutation, define calendar semantics and run manifest in Phase 04 |
| Momentum CSV reader and provider boundary | MIGRATE AFTER VALIDATION | PIT schema, immutable raw store, provider contract and quality tests |
| Momentum cost/report/metric code | MIGRATE AFTER VALIDATION | Decimal boundary, dated fees, benchmark alignment and formula golden tests |
| `quant_brain` account/portfolio concepts | REFERENCE ONLY | Replace with immutable domain model and append-only ledger in Phase 02 |
| Legacy fee and risk metric implementations | REFERENCE ONLY | Independent formulas and golden tests; do not copy current implementation |
| Tushare/BaoStock/Wind data wrappers | REFERENCE ONLY | Provider decision, official schema, PIT audit, rate-limit/error contracts |
| Qlib examples | REFERENCE ONLY | Adapter boundary only in Phase 09; core must not import Qlib |
| RL/FinRL notebooks and bundled datasets | REFERENCE ONLY | Separate research track, dataset license and leakage review |
| Factor examples | REFERENCE ONLY | FactorSpec, PIT universe, IC/RankIC and OOS experiment contract |
| Wind paper-trading scripts | DEPRECATE as runtime | Never run in CI; future broker adapter must use official docs and sandbox |
| Root `requirements.txt` | DEPRECATE as authoritative manifest | Replace through Phase 01 compatibility/lock decision; keep for legacy examples |
| `runtime/README.md` placeholder | DEPRECATE | Replace only when Phase 10/13 defines runtime ownership |
| `backup/` and duplicated tools/assets | DEPRECATE from active architecture | Provenance and consumer audit before any later removal |
| LLM/NLP, UI helper and online-platform examples | REFERENCE ONLY / OUT OF V1 | Separate ADR if scope is ever expanded |

## Explicit prohibitions

- Do not import legacy broker-facing code into the new runtime.
- Do not copy formulas merely because their current tests pass; formula tests are largely absent.
- Do not use current-only constituents for historical backtests.
- Do not execute with adjusted prices as if they were tradable prices.
- Do not infer broker fields, statuses, retry behavior, or idempotency from examples.
- Do not delete reference assets during migration until provenance, consumers and rollback are recorded.

## Planned-copy provenance checklist

Every later copied or derived unit must record:

1. source repository and immutable commit;
2. exact source path(s);
3. source license and retained notices;
4. target path and responsible Phase/ADR;
5. semantic changes, especially time, money, fees, fills and error handling;
6. deterministic tests and evidence command;
7. rollback/removal path.

No upstream runtime source is copied into the new package in Phase 00.
