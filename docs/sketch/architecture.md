# duel-master architecture sketch

## Current status

- We intentionally restarted from a clean scaffold on `dev`.
- The rejected implementation is preserved on `archive/current-impl`.
- The current branch now follows a flat MR2020 concern layout with a much slimmer duel runtime shell.

## Agreed constraints

1. The repository is an umbrella project named `duel_master`.
2. Runtime seams should be expressed through typed `affairon` affairs.
3. `duel_core` is a public boundary, not the true owner of authored MR2020 behavior.
4. MR2020 concern packages should own their own models, affairs, listeners, and local helpers.
5. Architecture must be validated through smoke-test-sized executable slices, not large speculative builds.
6. Unsupported areas should fail fast for now.
7. Every architecture shift must be persisted under `docs/sketch/`.

## Grounded current direction

### Public boundary

`duel_core` currently exports only `Duel`.

The public callable loop remains:

- `observe(view=...)`
- `available_actions()`
- `do(action)`

`Duel.state` currently returns the duel object itself for inspectable runtime access.

### Real ownership

The real implementation root is `src/duel_core/mr2020/`, organized as flat peer concerns:

- `duel/`
- `timing/`
- `phase/`
- `turn/`
- `player/`
- `card/`
- `draw/`
- `summon/`
- `battle/`
- `life_point/`
- `forbid/`
- `view/`

These are peers. `duel/` is not a parent owner for the other concerns.

### Concern ownership

- `duel/` owns duel bootstrap, bus shell, duel-loop anchor affairs, and public action collection.
- `timing/` owns timing-specific action bases and shared predicates.
- `phase/` owns `Phase`, phase transition affairs, and phase helper injection.
- `turn/` owns turn progression affairs plus current-turn helper injection.
- `player/` owns `Player`, `Deck`, `Zone`, `SetPlayers`, and player/current-player helper injection.
- `card/` owns `Card`, `RuntimeCard`, `REPRESENTATION`, `MoveCard`, and runtime card normalization.
- `draw/` owns draw affairs and draw planning listeners.
- `summon/` owns `NormalSummon` and summon-state helper injection.
- `battle/` owns `Attack`, battle availability, and battle resolution.
- `life_point/` owns `LpVary`, LP initialization, and LP mutation application.
- `forbid/` owns `Forbid`, forbid state helper injection, forbid policy, and the checked `do(...)` entrypoint.
- `view/` owns `PublicView`, `PublicPlayerView`, `PlayerView`, and injected `observe(...)`.

### Duel shell

Current runtime `Duel` is intentionally much thinner than before.

At runtime it directly owns only:

- `dispatcher`
- `emit`
- `available_actions()`
- construction/startup glue

Everything else is injected by concern listeners:

- players/current player → `player/`
- turn count → `turn/`
- phase → `phase/`
- normal summon state → `summon/`
- forbid state and `do(...)` → `forbid/`
- `observe(...)` → `view/`
- `opponent_of(...)` → `player/`

### Dispatch semantics

The two dispatch entry semantics are now intentionally split:

- `emit(...)` is raw dispatcher emission with no forbid check.
- `do(...)` is the duel action entrypoint injected by `forbid/` and performs forbid checks before delegating to `emit(...)`.

This means internal chained execution can use raw emission where appropriate, while player-visible actions keep one checked gate.

### Composition structure

Plugin composition is currently loaded from `[tool.affairon.profiles.duel]` in `pyproject.toml`.

There is no separate `plugins/` package and no separate `duel-runtime` profile.
Concern listeners are composed directly from their owning packages.

Cross-concern Pydantic rebuild ownership is still orchestrated from `mr2020.duel.bootstrap`, but each concern now contributes its own rebuild hook.

### Current affair vocabulary by owner

- `duel/affairs.py`
  - `DuelAffair`
  - `DuelAffairWithRequester`
  - `AvailableActions`
  - `CompletedAffair`
  - `MultiAction`
  - `DuelInit`
- `player/affairs.py`
  - `SetPlayers`
- `timing/affairs.py`
  - `ExposedUserAction`
  - `TimingAction`
  - `AtomicAction`
- `phase/affairs.py`
  - `EnterPhase`
  - `ExitPhase`
- `draw/affairs.py`
  - `Draw`
- `summon/affairs.py`
  - `NormalSummon`
- `battle/affairs.py`
  - `Attack`
- `life_point/affairs.py`
  - `LpVary`
- `card/affairs.py`
  - `MoveCard`
- `turn/affairs.py`
  - `AdvanceTurn`
- `forbid/affairs.py`
  - `Forbid`

### Current anchored duel flow

1. `Duel` is constructed from two `Player` objects and one explicit starting player.
2. `mr2020.duel.bootstrap` rebuilds the current model graph and composes concern listeners.
3. `SetPlayers` is emitted first.
4. `DuelInit` is emitted next.
5. Concern listeners inject player, phase, turn, summon, forbid, card, and view helpers/state.
6. Opening draws happen.
7. Initial life points are assigned by `life_point/`.
8. First-turn draw and first-turn battle entry are forbidden through `Forbid`.
9. `available_actions()` collects concern-contributed actions for the current duel state.
10. `do(action)` checks forbid policy and then delegates to `emit(action)`.
11. Concern listeners apply draw, summon, battle, life-point, phase, and turn behavior.
12. Completed work is surfaced through `CompletedAffair`.

### Validation target

The maintained validation target for this phase is one smoke flow at `tests/duel_core/test_smoke_duel_loop.py` proving:

- opening draws happen
- first-turn draw is skipped
- first-turn battle is unavailable
- phase progression works
- normal summon works
- turn rollover works
- turn-2 battle works
- LP changes happen through battle resolution
- observe output remains usable

## Superseded direction

The following are superseded for current implementation discussion:

- `duel_core/duel.py` as runtime owner
- `mr2020/affairs.py` as a central aggregate affair file
- `mr2020/plugins/` as the main ownership layout
- `battle/` owning LP mutation and LP initialization
- `Duel.do(...)` implemented directly in `duel/models.py`
- `Duel` directly owning players/current player/turn/phase/summon/forbid/view fields as its authored shape

## Open questions

1. Should rebuild orchestration stay in `duel/bootstrap.py`, or should concern modules eventually self-register more of that startup wiring?
2. Should shared predicates still live in `timing/`, or should some move into duel-loop or concern-local modules as the rule graph grows?
3. When should injected helper contracts become explicit package-local docs or declaration files rather than code-only convention?
