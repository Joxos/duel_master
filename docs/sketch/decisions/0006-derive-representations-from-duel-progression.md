# Decision 0006: derive representations from duel progression

Status: accepted
Date: 2026-03-17

## Decision

We will stop freezing abstractions ahead of evidence.

From now on, representations must be derived from an explicit narrated duel progression. If a duel step does not force a representation, do not add it.

## Required process

For each narrated duel step, record only:

1. what must already be true
2. what happens
3. what changes

Only introduce a new representation when one of those three cannot be expressed clearly.

## Status classes

- **Grounded**: directly forced by the traced duel progression
- **Provisional**: plausible, but not yet forced
- **Superseded**: older planning text that should no longer be treated as authoritative

## Consequences

- `0004` is provisional until the narrated duel walk forces its abstractions.
- `0005` remains grounded as a methodological rule about graph expression.
- Future discussions must cite the duel step that forced each new representation.
