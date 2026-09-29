# ADR-0003: Decimal accounting and explicit rounding

- Status: Accepted after Phase 02 independent Review GO
- Date: 2026-09-28
- Owners: Personal fork maintainer
- Related Phase: 02

## Context

Binary floats and ambient Decimal precision can change cash, cost basis or replay results. Historical A-share ticks and fees are not yet configured.

## Decision

Reject floats, including numeric JSON `$decimal` tags, non-finite values and fractional shares at domain boundaries. Keep price and caller-provided tick as Decimal; require alignment. Round CNY notional/postings and supplied fee to cents with `ROUND_HALF_UP`, under an explicit precision-50 context. Use context-independent `copy_negate`/`copy_abs` for signed postings. Retain residual cents in the remaining lot until final sale. Do not infer fees or ticks from symbol/board.

## Alternatives considered

- Float with epsilon: rejected because exact cash/journal conservation is required.
- Hard-coded 0.01 tick and current fee schedule: rejected because applicable historical rules vary and belong to dated rule configuration.

## Quant/data correctness impact

Rounded entries remain balanced, and repeated replay is stable. Caller must supply rule-correct tick/fee; incorrect but syntactically valid inputs cannot be certified in Phase 02.

## Reliability/safety impact

Invalid inputs fail closed. There is no live path, provider or broker connection.

## Migration and rollback

No old target-domain API or persisted state exists. Reverting this branch removes the new behavior only.

## Verification

Boundary, deterministic generated conservation, fractional-cent partial lot and low ambient precision tests in `tests/unit/test_domain_*.py`; `make all`.

## Consequences

Fee/tick configuration is mandatory in later execution-rule work. This phase models accounting semantics, not fee truth.
