# Decision 0004: thin shared effect IR and duel-bound runtime

Status: provisional
Date: 2026-03-17

## Decision

This note is provisional. It records a likely direction, but not a grounded commitment yet.

We may introduce a shared effect IR boundary, shared by master rules and future card effects.

If introduced, this IR should be named `EffectIR`. It must be fully semantic and must not contain processing detail.

We will not introduce a rich executable effect DSL at this stage.

If placeholders are needed, canonical `Duel` state should remain concrete and resolved. Placeholders should stay in transient specs only and be resolved by a duel-bound runtime context before final state mutation.

If collaborative seams are needed, duel execution dispatch should be duel-bound. Free-function listeners are the likely default. `AffairAware` class-bound listeners should be reserved for listeners that truly need stable injected collaborators or scoped lifetime management.

If this path survives the narrated duel walk, the runtime/orchestrator would resolve effect IR and emit action affairs while `Kernel` performs concrete duel mutation.

## Rationale

- Shared boundary shape should be fixed early so master rules and card effects do not diverge.
- A rich IR now would pull card-authoring concerns into `duel_core` too early.
- Unresolved placeholders inside canonical duel state would create a hidden second semantics layer.
- Duel-bound dispatch preserves duel isolation, replayability, and test clarity.
- Free functions keep first-slice rule listeners legible and reduce framework gravity.

## Thin IR split

1. `EffectIR`
   - declarative and unresolved
   - placeholders allowed
   - no processing detail allowed
2. `Resolved`
   - placeholder-resolved against current duel context
   - may directly reference concrete duel objects

## Consequences

- Placeholder vocabulary must be designed together with a duel-bound resolver.
- `Duel` should expose concrete facts only.
- The runtime/orchestrator, not the `Duel` data object itself, owns dispatch and placeholder resolution.
- Kernel mutation remains downstream from affair emission.
- We can still reuse one effect IR across master rules and card effects without overcommitting to a DSL.
