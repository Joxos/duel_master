# substrate

The `substrate` package is the low-level causal execution foundation.

It should eventually host generic runtime pieces such as typed events, queries,
opportunities, reducers, ordered dispatch, and deterministic queue/procedure
execution.

## MUST DO

- Define generic execution primitives that are not Yu-Gi-Oh specific.
- Support typed multi-handler collaboration with deterministic ordering.
- Support reducer-driven result composition instead of ad hoc dict merges.
- Support runtime tracing and replay-friendly deterministic sequencing.

## MUST NOT DO

- Must not contain card names, duel phases, or Yu-Gi-Oh terminology.
- Must not commit duel-specific legality logic.
- Must not directly inspect card databases or duel state schemas.
- Must not become a second rules layer hidden under generic names.

## Borrowing Notes

- From `affairon`: seam-as-contract, ordered collaboration, aggregation.
- From `moduvent`: event-class ergonomics and queue/runtime intuition.
- Not borrowing wholesale: generic plugin CLI concerns, direct dict-merge as the
  core reduction model, or application-level event framing.
