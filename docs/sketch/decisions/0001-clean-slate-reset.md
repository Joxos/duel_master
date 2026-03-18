# Decision 0001: clean-slate reset and persistence workflow

Status: accepted
Date: 2026-03-17

## Decision

We reset active development to a fresh scaffold on `dev` and archived the rejected implementation on `archive/current-impl`.

We also adopted the following persistence workflow:

- `docs/sketch/architecture.md` stores the current architecture draft.
- `docs/sketch/sessions/` stores session notes.
- `docs/sketch/decisions/` stores durable accepted decisions.

## Consequences

- Future agents must align with persisted discussion before implementing.
- Architecture drift should be easier to detect in review.
- We accept a slower start in exchange for stronger continuity and fewer context-loss regressions.
