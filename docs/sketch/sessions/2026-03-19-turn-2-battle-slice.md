# Session note: turn-2 battle slice

Date: 2026-03-19
Branch: `dev`

## Trigger

The next grounded executable path after the minimal normal summon slice was the
first real Battle Phase path on turn 2.

## What changed

- Added a minimal `Attack` executable affair with attacker card and optional defender card.
- `Kernel` now resolves one battle with no chains and no position system, including direct attacks when the defending field is empty.
- Battle results are now expressed through concrete affairs:
  - `SendToGraveyard`
  - `LpVary`
- `CompletedAffair` returns to its minimal role of marking executable completion.
- `Player` now owns minimal battle-forced runtime state:
  - `graveyard`
  - `life_points`
- `DuelState` now owns turn-scoped attack tracking through `attacked_zones`.
- `mr2020` now contributes battle actions only during `Battle` and only for attacker/target pairs that currently exist.

## Why this is architecture-consistent

- Battle legality remains authored in `mr2020`.
- Battle mutation and resolution remain owned by `Kernel`.
- `Duel` still only exposes the same public loop:
  - `observe(view=...)`
  - `available_actions()`
  - `do(action)`
  - `emit(affair)`
- New state was only added where the narrated battle path could not be expressed without it.
- Battle result ownership now follows emitter/handler boundaries instead of dictionary payloads.

## Scope boundary

This slice still does not model:

- battle position
- defense-position calculation
- chain timing
- Damage Step substeps
- triggered effects

## Verification target

The smoke path for this slice is:

1. player 1 summons and ends
2. player 2 draws, summons, enters battle
3. player 2 attacks player 1's monster or attacks directly if the field is empty
4. the duel returns to the same action loop with updated zones, graveyard, and LP
