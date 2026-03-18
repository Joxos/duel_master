# Session note: executable affair step 2 implementation

Date: 2026-03-18
Branch: `dev`

## Trigger

After recording the next direction around `ExecutableAffair`, `MultiAffair`,
Kernel-owned `State`, and `CompletedAffair`, the user asked to implement that
step first and explicitly defer config-driven setup until later.

## Scope kept for this step

This implementation step intentionally included:

- removing the old `Action` wrapper
- returning executable affairs directly from `available_actions()`
- making `Duel.do(...)` submit execution through an execution-request affair
- moving current runtime state under `Kernel`
- emitting `CompletedAffair` after execution

This implementation step intentionally did not include:

- config-driven affairon plugin composition
- replacing the current hardwired MR2020 setup call
- richer contradiction resolution beyond the current permissive behavior
- a real gameplay use case for `MultiAffair`

## Implemented changes

### Runtime and public surface

- added `State` as the minimal runtime model for the current slice
- `Kernel` now owns that runtime state
- `Duel` now exposes query properties over `Kernel.state` instead of storing
  writable runtime fields directly

### Execution-facing affairs

- added `ExecutableAffair`
- added `ExecutionRequest`
- added `CompletedAffair`
- added `MultiAffair`
- `AvailableActions.actions` now collects executable affairs directly

### Public action flow

- `available_actions()` now returns collected `ExecutableAffair` instances
- `Duel.do(...)` now validates membership and emits `ExecutionRequest`
- `Kernel` executes the submitted executable affair
- `Kernel` emits `CompletedAffair` after execution completes

### Listener contributions

- MR2020 listeners no longer build wrapper actions through a `Duel` helper
- they now contribute concrete executable affairs directly

## Preserved behavior

- `available_actions()` remains dispatcher-driven and query-only
- forbids still use callable identity through `requester` and `Forbid.target`
- current end-turn progression still reaches the next draw phase
- CLI still works through `observe / available_actions / do`

## Verification

- `uv run pytest tests/duel_core/test_observe_available_actions_do.py`
- `uv run pytest tests/duel_core/test_opening_draw_flow.py`
- `uv run pytest tests/duel_core/test_turn_cleanup_flow.py`
- `uv run pytest tests`
- `uv run ruff check src tests`
- `uv run basedpyright src tests`

All passed.

## Deferred next step

Config-driven setup remains the next deferred step. The code still hardwires
MR2020 registration even though `pyproject.toml` already declares the local
plugin target.
