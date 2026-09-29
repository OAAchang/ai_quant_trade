# ADR-0004: Append-only domain events and balanced derived journals

- Status: Accepted after Phase 02 independent Review GO
- Date: 2026-09-28
- Owners: Personal fork maintainer
- Related Phase: 02

## Context

Snapshots alone lose auditability and cannot prove recovery. Phase 02 has no database or broker adapter.

## Decision

Use a controlled in-memory `Account` aggregate. Its append-only event sequence contains funding, placement, status and fill records. Apply on copied maps/tuples and commit only after all validation. Identical event/fill IDs are idempotent, conflicting IDs fail. Funding and fills produce balanced signed-debit journal entries; snapshots are projections reconstructed by `Account.replay`.

## Alternatives considered

- Mutable balance/position as source of truth: rejected because replay/reconciliation would be impossible.
- Introducing a database now: deferred because storage, migrations and crash recovery belong to Phase 10.

## Quant/data correctness impact

Cash/lot conservation and replay equivalence are directly testable. Partial lot cost basis carries rounded remainder. Market value is intentionally absent without a priced as-of source.

## Reliability/safety impact

Duplicate fills cannot debit cash twice. Rejected appends are atomic in memory. This does not provide cross-process durability, broker reconciliation or real-order safety; those remain hard gates.

## Migration and rollback

Schema v1 is the first target-domain schema. Unknown versions are rejected; future storage changes require explicit migration and rollback plan. Revert this branch to remove the new in-memory model.

## Verification

Deterministic generated conservation/replay/idempotency tests, negative cash/oversell tests, `make all`, independent Review.

## Consequences

The semantic aggregate is intentionally small and single-account/CNY. Real storage and operational recovery cannot reuse it unmodified as a live OMS.
