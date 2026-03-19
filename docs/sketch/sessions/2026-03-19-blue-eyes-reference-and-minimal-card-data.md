# Session note: Blue-Eyes reference and minimal card data

Date: 2026-03-19
Branch: `dev`

## Trigger

The next requested step after the minimal normal summon slice was:

- fix the latest review comments around guarded execution and public view shape
- introduce an authoritative card-info fetch script before implementing a real card
- add Blue-Eyes White Dragon as the first real card reference without jumping to
  a full tribute summon slice

## What changed

- `EnterPhase` and `Forbid` now both travel through the guarded Kernel execution
  registration path expected by the current review comments.
- `PublicView` now carries fixed public facts for:
  - current player
  - opponent
  - current turn
  - phase
  - normal summon used
- A card-info fetch script now exists under `examples/card_info_fetch.py`.
- Blue-Eyes White Dragon reference data is now stored locally under
  `docs/references/cards/blue_eyes_white_dragon.json`.
- Runtime card handling moved from raw `str` tokens to a minimal frozen `Card`
  model sufficient for identity plus printed facts.

## Blue-Eyes scope boundary

Blue-Eyes is now present as the first real card reference and runtime card data.

That does **not** mean the current slice supports legal Blue-Eyes normal summon.
The current normal summon slice still only supports monsters that are directly
normal summonable under the current simplified rules, which is modeled as
`level <= 4`.

This is intentional. A legal Blue-Eyes summon would force a tribute summon slice
and a richer field model, which are both out of scope for this step.

## Why this is still architecture-consistent

- External card data remains reference-only and is not treated as raw runtime
  payload.
- Runtime semantics still flow through the current affair/kernel seams.
- The first real card does not introduce a new custom behavior system.
- The new representation was forced by the need to distinguish summonable vs.
  non-summonable cards and preserve printed facts accurately.

## Verification

- `uv run pytest tests`
- `uv run ruff check src tests`
- `uv run basedpyright src tests`

All passed.
