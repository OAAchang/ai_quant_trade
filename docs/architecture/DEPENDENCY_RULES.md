# Target-package dependency rules

The package under `src/ai_quant_trade/` is the new target core; all other upstream Python trees remain reference-only. ADR-0001 defines the migration, and ADR-0002 defines the Phase 01 tooling boundary. This document describes **allowed imports**, not implemented trading capability.

| Importing layer | May import from target-package layers |
|---|---|
| `domain` | `domain` only; standard library only |
| `ports` | `ports`, `domain` |
| `application` | `application`, `ports`, `domain` |
| `adapters` | `adapters`, `application`, `ports`, `domain` |
| `research` | `research`, `application`, `ports`, `domain`; never concrete broker adapters |
| `runtime` | `runtime`, `application`, `ports`, `domain`, `adapters`, `research` |
| `cli` | Other layers only as a safe composition/operator edge |

`settings` and `logging` are outer configuration/observability modules; only `runtime` and `cli` may import them. The package root exposes a version only. All target-package imports must be absolute; relative imports are rejected to keep the AST check unambiguous. `domain` additionally rejects common data, I/O, database, network and broker libraries. No legacy source is imported by the target package.

Run `make security` or `python scripts/check_boundaries.py`. The check parses source without executing it and fails on outward imports. Unit tests include a deliberately illegal `domain → adapters` example and a root-alias bypass example. Dynamic imports, reflection and arbitrary side effects are not fully provable by this static check; code review remains required.

The layer directories are empty boundaries in Phase 01. They are **not** evidence that a backtest, provider, OMS, risk engine, paper broker or live adapter exists. Research must never gain broker submit/cancel access; application use cases will use ports, and adapters will be introduced only in their authorized later phases.
