# Session note: IR, placeholder resolution, and affair ownership

Date: 2026-03-17
Branch: `dev`

## What was clarified

- Master rules and card effects should share one thin effect IR boundary.
- The shared base name should be `EffectIR`, not `EffectBlueprint`.
- That IR should be fully semantic and should not yet become a rich executable DSL.
- Canonical `Duel` state should remain concrete.
- Placeholders such as self / opponent / this card / controller belong in transient specs, not in persisted duel state.
- Placeholder resolution should be performed by a duel-bound runtime context.
- Duel execution affairs should be emitted by a duel-bound runtime/orchestrator, not by a process-global dispatcher.
- Kernel, not runtime, performs concrete duel mutation and contradiction handling.
- Free-function listeners are the default for first-slice rule semantics.
- `AffairAware` class-bound listeners remain available for stateful collaborators or scoped registrations.
- `ObserveCurrentFacts` was rejected for the first slice because runtime can read concrete duel facts directly.
- The first slice should be rooted in runtime entrypoints and only use affairs where collaboration is actually needed.

## Why this matters

These choices determine whether later implementation stays readable and replayable or drifts into a bus-first, DSL-first, or hidden-late-binding design.

## Key warning captured

The dangerous version of this design is to let unresolved placeholders survive deep into execution or to let affairs appear as active agents. Both would blur ownership of state mutation and make debugging much harder.
