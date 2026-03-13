# kernel

The `kernel` package owns duel-specific machinery, not duel semantics.

Kernel is responsible for state storage, deterministic action commit, hidden
information boundaries, primitive operations, and fixpoint-style cleanup loops.

## MUST DO

- Own canonical duel state mutation and state snapshots.
- Expose primitive operations such as draw, move, summon, destroy, and pay LP.
- Provide deterministic sequencing for action commit and replay reproduction.
- Keep hidden-information projection and replay-safe tracing coherent.

## MUST NOT DO

- Must not encode Master Rules directly as if/else flow logic.
- Must not encode card-specific legality or timing text.
- Must not decide gameplay semantics that can live in unified rules.
- Must not absorb query/modifier/event semantics that belong in substrate.

## Design Reminder

If a behavior can be phrased as "allowed, forbidden, replaced, modified,
triggered, or procedurally inserted," it probably belongs in `rules`, not here.
