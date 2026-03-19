# Session note: review alignment for card rules and CLI view

Date: 2026-03-19
Branch: `dev`

## Trigger

Review feedback called out four architecture-alignment issues:

- `extra_deck` should not be modeled as a draw-capable `Deck`
- card data should not own current-slice summonability rules
- the CLI should render against the public view shape and show both monster zones
- Blue-Eyes White Dragon should live under `src/cards/` as canonical runtime card data

## What changed

- `Player.extra_deck` now models extra-deck contents as `list[Card]` instead of `Deck`.
- The current-slice normal-summon check moved out of `Card` and back into `mr2020.py`, where authored rules already live.
- Blue-Eyes White Dragon now lives directly at `src/cards/blue_eyes_white_dragon_89631139.py` as a plain card constant, without wrapper builders.
- `duel_core/testing.py` was removed rather than preserved as a stale helper layer.
- `PublicView` is back to holding only public duel facts.
- `PlayerView` now carries access-controlled player-facing snapshots for the viewer, the opponent, and the current player.
- The stale `tests/` files were removed instead of being kept as false confidence during the MVP rewrite.

## Why this is architecture-consistent

- `Card` is back to being printed/runtime card data rather than a container for authored rule judgments.
- Rule-specific logic remains in the listener-driven `mr2020` seam instead of leaking into models or `Kernel`.
- The extra deck no longer advertises draw behavior that the current slice does not use.
- Canonical card data now has one runtime source of truth while still staying separate from external reference JSON.
- `observe(...)` now enforces a tighter access-control boundary instead of returning full opponent runtime entities.
- The cleanup removed migration and helper layers instead of preserving them for compatibility.

## Verification

- Validation for this cleanup should use lint, type checks, build, and direct smoke/manual execution rather than relying on the removed stale tests.
