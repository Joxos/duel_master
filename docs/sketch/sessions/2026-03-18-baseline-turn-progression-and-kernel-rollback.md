# Session note: baseline turn progression and kernel rollback

Date: 2026-03-18
Branch: `dev`

## Trigger

After reconsidering the previous direction, the user chose to roll back the
recent Kernel execution seam changes that had been completed but were not yet a
meaningful part of the modeled slice.

The new priority is to keep pushing the duel model forward first:

- basic baseline turn progression
- per-turn phase-advance chances through available actions
- first-turn battle restriction expressed through `Forbid`

## Rollback recorded here

The following recent changes were intentionally rolled back:

- the internal Kernel execution dispatcher seam
- the extra module introduced only to prove that seam
- tests that existed only to prove the seam itself

The branch keeps:

- `Duel.state`
- `ExecutableAffair`
- `ExecutionRequest`
- `CompletedAffair`
- current callable-target `Forbid` pattern

## New modeled slice

The current modeled turn surface is now:

- `Draw`
- `Standby`
- `Main Phase 1`
- `Battle`
- `Main Phase 2`
- `End`

This is still intentionally small. It does not yet include broader OCG systems
such as chains, fast-effect timing, summon procedure, or field interaction.

## How progression is modeled now

- turn progression is still driven by `EnterPhase`, `TurnCleanup`, and
  `AvailableActions`
- each turn's actionable progression is surfaced through `available_actions()`
- `MAIN_1` can always advance to `End`
- `MAIN_1` can advance to `Battle` only when not forbidden
- `Battle` advances to `Main Phase 2`
- `Main Phase 2` advances to `End`
- entering `End` now directly advances control to the next player's `Draw`

## First-turn battle restriction

- the first player's first turn cannot enter the Battle Phase in this slice
- that restriction is modeled through `Forbid`
- this mirrors the existing first-turn draw restriction pattern and keeps the
  representation grounded in current affairs rather than introducing a new
  special-purpose abstraction

## Reason for the direction change

The user explicitly chose modeling progress over pre-emptive refactoring.

The current branch should therefore prefer:

1. the smallest concrete rulebook-grounded progression slice
2. more executable examples of phase flow
3. postponing refactor decisions until the modeled slice shows real pressure

## Verification

- `uv run pytest tests`
- `uv run ruff check src tests`
- `uv run basedpyright src tests`

All passed.
