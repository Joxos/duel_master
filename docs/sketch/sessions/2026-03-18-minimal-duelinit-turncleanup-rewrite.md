# Session note: minimal DuelInit / TurnCleanup rewrite

Date: 2026-03-18
Branch: `dev`

## Trigger

The user rejected the current implementation shape and supplied a smaller semantic sketch to follow directly.

Key intended logic from the user:

- on `EnterPhase(DRAW)`, MR2020 emits `Draw(player=current_player, num=1, requester=turn_draw)`
- on `DuelInit`, MR2020 emits opening `Draw` for both players
- on `DuelInit`, MR2020 emits `Forbid(target=turn_draw, outdated_when=TurnCleanup(turn=current_turn+1))`
- `TurnCleanup` is emitted automatically after `ExitPhase(END)` and before the next `EnterPhase(DRAW)`
- CLI should use `observe / available_actions / do`

## Rewrite outcome

The previous runtime/effect-compiler/plugin-loading slice was replaced with a smaller implementation centered on:

- `DuelInit`
- `EnterPhase`
- `ExitPhase`
- `Draw`
- `Forbid`
- `TurnCleanup`

Public `Duel` usage now exposes:

- `observe(view=...)`
- `available_actions()`
- `do(action)`
- `emit(affair)`

## Preserved boundary

- `Duel` remains the public facade.
- affairs remain listener-driven.
- `Kernel` remains the concrete mutation/filter point.
- rule semantics remain authored in listeners rather than handwritten in `Kernel` branches.

## Removed as unrelated to this slice

- `DuelRuntime`
- effect compiler pipeline
- plugin loader
- previous runtime ownership scaffolding
- previous draw-to-standby action shape

## Verification

- focused rewrite tests passed
- full `pytest tests` passed
- `ruff check src tests` passed
- `basedpyright src tests` passed
- CLI still ran correctly
