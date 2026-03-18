# Decision 0002: start from Master Rules before full duel-state modeling

Status: accepted
Date: 2026-03-17

## Decision

We will start planning from authoritative OCG Master Rule 2020 materials before attempting full duel-state modeling.

## Rationale

- Starting from state-first modeling risks overmodeling.
- It also risks encoding subjective assumptions before official timing and legality boundaries are pinned down.
- Master Rules are the right source for the initial vocabulary of windows, opportunities, legal action categories, and primitive outcomes.

## Consequences

- We should extract a compact official-rules glossary first.
- We should only derive the minimum state facts needed by the first smoke path.
- Unsupported areas should remain explicit and fail fast.
- Card-local authored semantics remain deferred until the baseline rule path is stable.
