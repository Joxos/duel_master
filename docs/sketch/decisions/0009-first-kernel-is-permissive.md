# Decision 0009: first Kernel is permissive

Status: accepted
Date: 2026-03-17

## Decision

For the first implementation slice, `Kernel` is a permissive pass-through filter plus concrete mutation point.

It does not yet implement contradiction resolution, allow/forbid precedence, or broader downstream timing ownership.

## Rationale

- The currently traced flow does not yet force conflict resolution logic.
- A blank filter preserves the future expansion point without prematurely authoring final adjudication behavior.

## Consequences

- First-slice code may route selected actions through `Kernel` even though `Kernel` currently allows them by default.
- Future traced conflict cases may expand `Kernel` responsibilities later.
