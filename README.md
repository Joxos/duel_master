# duel_engine

`duel_engine` is a library for modeling Yu-Gi-Oh duel state and procedure.

This repository is currently organizing toward a stricter architecture split so
that agent-driven development does not smear responsibilities across layers.

## Architecture Overview

```text
src/duel_engine/
  substrate/   # generic causal/rule execution substrate
  kernel/      # duel-specific state commit and primitive operations
  rules/       # MR2020 rules and card rules in unified rule IR
  cards/       # card definitions and card-authored rule bundles
```

## Current Direction

- Master Rules and card rules should converge into a unified rule layer.
- Event/query/modifier/procedure mechanisms should be extracted into substrate,
  not mixed directly into duel flow or card definitions.
- Concrete Yu-Gi-Oh scenarios in `examples/` are preferred over abstract API
  debates, so architecture can be validated against real interactions early.

## Borrowed Ideas Under Evaluation

The project is explicitly evaluating ideas from two Joxos projects:

- `affairon`
  - Borrowing: typed seam/contract, ordered multi-handler collaboration,
    result aggregation, plugin-oriented composition.
  - Intended use here: foundation for typed rule/query/opportunity seams.
- `moduvent`
  - Borrowing: event classes, queue-oriented runtime thinking, lightweight
    subscription ergonomics, module discovery lineage.
  - Intended use here: foundation for deterministic event/procedure dispatch.

These projects are not being copied wholesale. Their strengths are being
evaluated as substrate ingredients.

## Validation Strategy

Before stabilizing a public architecture API, examples should prove that the
layers cooperate correctly in concrete Yu-Gi-Oh scenes such as:

- default Draw Phase progression
- battle-phase prohibition this turn
- activation that cannot be responded to
- continuous rule changes like "cannot draw"
