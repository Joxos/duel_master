# Session note: bus-only Duel, life_point split, and SetPlayers refactor

Date: 2026-04-13
Branch: `dev`

## Trigger

The previous flat-concern refactor fixed package ownership, but still left too much runtime ownership on `Duel`.

The next requested step was:

- split `life_point` out of `battle`
- introduce `SetPlayers` for delayed player injection
- slim `Duel` further so it keeps only bus-related responsibilities
- separate raw `emit(...)` from forbid-checked `do(...)`

## What changed

- Added `src/duel_core/mr2020/life_point/`.
- Moved `LpVary`, LP init, and LP mutation application into `life_point/`.
- Added `src/duel_core/mr2020/player/affairs.py` with `SetPlayers`.
- Changed `Duel` startup to emit `SetPlayers` before `DuelInit`.
- Removed direct player bootstrap fields from `Duel.__init__`.
- Moved checked `do(...)` ownership into `forbid/listeners.py`.
- Treated `emit(...)` as the raw dispatcher alias on `Duel`.
- Injected helper methods from concerns instead of keeping those members authored on `Duel`:
  - `get_players`, `get_current_player`, `set_current_player`, `opponent_of`
  - `get_current_turn_count`, `set_current_turn_count`
  - `get_phase`, `set_phase`
  - `get_normal_summon_used`, `set_normal_summon_used`
  - `get_active_forbids`
  - `observe`
  - `do`
- Updated smoke test and CLI to use the injected helper surface.

## Why this is closer to the intended model

- `Duel` is now much closer to a bus shell than a disguised runtime owner.
- LP is no longer hiding inside battle.
- Player setup is no longer an implicit constructor-side stash; it has its own affair.
- `emit(...)` and `do(...)` now express two different semantics instead of one mixed entrypoint.

## Verification

This refactor was verified with:

- `uv run pytest tests`
- `uv run ruff check src tests`
- `uv run basedpyright src tests`
- `uv build`

## Remaining pressure points

- `duel/bootstrap.py` still orchestrates rebuild assembly.
- `timing/predicates.py` still knows about duel-loop completion shapes.
- The injected helper contract is currently expressed in code and type declarations, not yet in package-local README notes.
