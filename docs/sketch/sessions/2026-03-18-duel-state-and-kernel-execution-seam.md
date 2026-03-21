# Session note: duel state surface and kernel execution seam

Date: 2026-03-18
Branch: `dev`

## Trigger

After reviewing the current facade and execution structure, the user chose
consistency over convenience and asked for two immediate changes while the
project is still small:

- make `Duel.state` the explicit raw state access surface and remove the old
  convenience proxies on `Duel`
- introduce an internal dispatcher seam inside `Kernel` early, before execution
  logic grows large

## Scope kept for this step

This step intentionally included:

- adding `Duel.state`
- migrating existing callers from `duel.players/current_player/current_turn/phase`
  to `duel.state.*`
- removing those old proxy properties from `Duel`
- adding a Kernel-internal execution dispatcher seam

This step intentionally did not include:

- merging `DuelView` into `DuelState`
- moving authored rule plugins into Kernel internals
- introducing new public affair types
- broadening contradiction-resolution semantics

## Implemented changes

### Public state surface

- `Duel` now exposes raw runtime state through `Duel.state`
- old convenience proxies for `players`, `current_player`, `current_turn`, and
  `phase` were removed
- MR2020, CLI, and tests were migrated to explicit `duel.state.*` access

### Preserved observe boundary

- `observe(view=...)` still returns `DuelView`
- `DuelView` remains a view/projection model, not the runtime state object
- render-facing access and raw runtime access remain separate

### Kernel execution seam

- `Kernel` now owns an internal execution dispatcher
- the outer duel dispatcher still handles authored rules, setup, available
  action collection, and other semantic collaboration
- the internal kernel package now owns planning and apply collaborators for
  execution-facing concerns that should not accumulate directly in `Kernel`

### Current split

- outer dispatcher still directly handles authored rule semantics such as MR2020
  listeners and `Draw` as a semantic affair
- internal execution dispatcher currently handles:
  - `ExitPhase`
  - `MultiAffair`

This split is intentionally narrow. It establishes the seam without moving rule
semantics or breaking the current public `emit(affair)` escape hatch.

## Result

- raw state access is now explicit and consistent
- `Duel` remains the public facade, but no longer carries redundant state
  convenience properties
- `Kernel` now has an internal execution seam that can grow without turning the
  class itself into the only place where execution logic lives

## Verification

- `uv run pytest tests`
- `uv run ruff check src tests`
- `uv run basedpyright src tests`

All passed.
