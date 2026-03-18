# Decision 0011: minimal DuelInit / Draw / TurnCleanup slice

Status: accepted
Date: 2026-03-18

## Decision

The current executable slice is rewritten around the smallest semantic flow directly sketched by the user:

- `DuelInit`
- `EnterPhase`
- `ExitPhase`
- `Draw`
- `Forbid`
- `TurnCleanup`

Public usage is now kept to:

- `observe(view=...)`
- `available_actions()`
- `do(action)`
- `emit(affair)`

`available_actions()` is dispatcher-driven in this slice: it asks a dedicated `AvailableActions` affair and returns listener-contributed actions.

## Boundary

- `Duel` remains the public facade.
- Rule semantics are authored in listeners.
- `Kernel` remains the concrete mutation/filter point for emitted affairs.
- User actions are separated from internal affairs:
  - `do()` is for user-selectable actions
  - `emit()` is for dispatcher affairs
- Actionable in-game affairs carry `requester` so semantic origin can be distinguished by rules and forbids.

## Consequences

- The previous runtime/effect-compiler/plugin-loading shape is not kept for this slice.
- MR2020 is expressed only in the tiny callback form forced by the traced flow:
  - initial draw
  - turn draw
  - initial-turn forbid
- The current implementation only supports one current actor at a time.
- The current phase surface is intentionally minimal.
