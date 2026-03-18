# Session note: dispatcher-driven available actions and requester inheritance

Date: 2026-03-18
Branch: `dev`

## Trigger

The user rejected the remaining hardcoded action-availability logic in `Duel.available_actions()` and asked for:

- dispatcher-driven action collection through an affair
- listener-owned action validity checks
- shared `requester` inheritance for actionable in-game affairs such as `EnterPhase`

## Implemented refinement

### Available actions

- added `AvailableActions`
- `Duel.available_actions()` now only:
  - creates the affair
  - emits it
  - returns the collected actions
- listeners now append valid current actions into the affair instead of `Duel` hardcoding them

### Requester inheritance

- added `ActionableDuelAffair`
- `EnterPhase`, `ExitPhase`, and `Draw` now inherit `requester`
- non-actionable affairs such as `DuelInit`, `Forbid`, and `TurnCleanup` remain plain duel affairs

## Collection shape choice

Instead of merge-strategy-based dict collection, this refinement uses a mutable accumulating affair with `actions: list[Action]`.

This was chosen because it is the smallest clean structure for the current slice:

- no nested merge normalization
- no synthetic result dict unpacking in `Duel`
- listeners can contribute multiple actions directly if needed later

## Result

- public `available_actions()` is now query-only
- semantic action availability lives in listeners
- forbids and rules can distinguish semantic source through `requester`

## Verification

- focused dispatcher/requester tests passed
- full `pytest tests` passed
- `ruff check src tests` passed
- `basedpyright src tests` passed
