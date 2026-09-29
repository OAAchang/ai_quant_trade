# ADR-0005: Explicit order reports, UNKNOWN and conservative reservations

- Status: Accepted after Phase 02 independent Review GO
- Date: 2026-09-28
- Owners: Personal fork maintainer
- Related Phase: 02

## Context

Submission/ACK does not prove execution. Network timeout can leave broker state unknown; a blind retry risks duplicate orders.

## Decision

Model `NEW`, `SUBMITTED`, `ACK`, `PARTIALLY_FILLED`, `FILLED`, `CANCELLED`, `REJECTED`, `EXPIRED`, `UNKNOWN` with checked transitions. Only a distinct `Fill` advances executed quantity. UNKNOWN retains an open order and its sell reservation; no retry inference. Terminal orders reject later fills. The aggregate stamps local placement time; the `SUBMITTED` event is local request dispatch and stamps submission time. A fill executed before either is rejected even if observed later. ACK observation is not used as a lower bound. Late, contradictory or out-of-order reports fail closed for later reconciliation.

## Alternatives considered

- Treat ACK as filled: rejected because it would fabricate holdings/cash.
- Retry UNKNOWN automatically: rejected because duplicate real orders could result.
- Guess a broker's state mapping now: rejected because no broker or official API is selected.

## Quant/data correctness impact

Partial fills update cash and lots only for executed quantity. Open sell orders reserve remaining shares; same-day unsellable lots cannot back a sell order.

## Reliability/safety impact

No live adapter exists. The in-memory state machine does not persist requests, query a broker or reconcile an incident; Phase 10+ must do that before any real submission.

## Migration and rollback

No prior target-domain order API exists. Schema v1 rejects unknown versions. Reverting the branch restores the empty domain boundary.

## Verification

Positive/negative transitions, UNKNOWN, duplicate fill, partial fill, cancellation/rejection and reservation tests; `make all`; independent Review.

## Consequences

A broker-specific gateway must map reports to these semantics and handle contradictory/late reports through a reconciliation workflow, not by silently reordering history.
