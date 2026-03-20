# Decision 0012: executable affairs and kernel-owned state direction

Status: accepted
Date: 2026-03-18

## Decision

The next implementation direction will model user-selectable execution around
`ExecutableAffair` rather than the current `Action` wrapper.

`Kernel` will own the internal runtime `State` and the execution lifecycle for
submitted executable affairs.

## Core direction

- `Duel` remains the public facade and composition root.
- Rule setup should be config-driven through affairon plugin composition rather
  than hardwired rule setup calls.
- The shared execution-facing base is `ExecutableAffair`.
- `MultiAffair` is a concrete `ExecutableAffair` for ordered composition of
  multiple child affairs.
- `Forbid` remains an affair, but not an `ExecutableAffair`.

## Public boundary

- `available_actions()` remains query-only.
- It should collect and return currently available executable affairs through a
  dispatcher-driven collection seam.
- `Duel.do(...)` should accept any `ExecutableAffair`.
- `Duel.do(...)` should submit an execution request into the dispatcher and stop
  there.
- `emit(affair)` remains the lower-level public escape hatch for direct affair
  submission where that boundary is still needed.

## Kernel boundary

`Kernel` should own:

1. runtime `State`
2. contradiction and priority resolution
3. interpretation of executable affairs into concrete execution steps
4. emission of `CompletedAffair(action: ExecutableAffair, result: DuelAffair)` after execution

`Duel` should expose query access over runtime state rather than keep writable
runtime state as its own direct surface.

## Forbid rule

`Forbid.target` should continue to point at a specific callable identity.

This is required because multiple semantic sources may emit the same affair
type. Source identity, not only affair type, must remain distinguishable.

## MultiAffair rule

- `MultiAffair` is submitted unchanged through `Duel.do(...)`.
- `Kernel` treats `MultiAffair` as one executable affair during conflict and
  priority checks.
- `Kernel` only expands `MultiAffair` into ordered child affairs during the
  actual execution stage.

## Completion loop

Execution completion should re-enter the same gameplay loop:

1. available executable affairs are collected
2. one executable affair is submitted
3. `Kernel` resolves and executes it
4. `CompletedAffair` is emitted
5. newly opened trigger windows return to `available_actions()` collection

## Testing consequence

For the current rapid-iteration phase, the maintained validation target is one
smoke flow that proves:

- executable choices are surfaced correctly
- player selection can advance duel progression

Broader tests may return later, but are not the primary maintenance target for
this phase.

## Replacement and alignment

- This decision replaces the current role of the temporary `Action` wrapper as
  the intended long-term execution model.
- This decision also replaces the earlier `DuelRuntime` record as the durable
  next direction for runtime ownership.
- `0011` remains the record of the current minimal public flow.
