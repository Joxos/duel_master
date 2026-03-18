# Decision 0008: Kernel owns final resolution and downstream timing

Status: partially accepted
Date: 2026-03-17

## Decision

`Kernel` is the final concrete mutation owner.

Its current first-slice grounded responsibilities include:

1. acting as a permissive pass-through filter
2. applying concrete duel mutation

Contradiction resolution, allow/forbid precedence, and downstream timing ownership remain provisional expansion targets.

## Boundary

This does not mean `Kernel` should author semantic rule content itself.

- Rule and effect listeners still contribute semantics
- `Duel` still organizes collaboration and submission
- `Kernel` currently applies concrete mutation after a permissive filter step
- Strong final-resolution behavior should not be frozen onto `Kernel` until traced conflict cases actually force it.

## Consequences

- The first implementation can keep `Kernel` minimal while preserving a clear expansion point.
- Final contradiction handling and downstream timing ownership remain open pending traced cases.
