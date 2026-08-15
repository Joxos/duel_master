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

- `observe(player)`
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

- `duel/` owns duel bootstrap, bus shell, duel-loop anchor affairs, `ProviderRegistry`, `MultiAction` execution, and public action collection.
- `timing/` owns timing-specific action bases and shared predicates.
- `phase/` owns `Phase`, `PhaseRuntime`, phase transition affairs.
- `turn/` owns `TurnRuntime`, `AdvanceTurn`, and turn progression.
- `player/` owns `Player`, `Deck`, `Zone`, `PlayerRuntime`, `SetPlayers`.
- `card/` owns `Card`, `RuntimeCard`, `REPRESENTATION`, `MoveCard`, and runtime card normalization.
- `draw/` owns draw affairs and draw planning listeners.
- `summon/` owns `NormalSummon`, `SummonRuntime`.
- `battle/` owns `Attack`, battle availability, and battle resolution.
- `life_point/` owns `LpVary`, LP initialization, and LP mutation application.
- `forbid/` owns `Forbid`, `ForbidRuntime`, forbid policy. `ForbidRuntime.do(...)` is the checked action entrypoint.
- `view/` owns `PublicView`, `PublicPlayerView`, `PlayerView`, `ViewRuntime`.

### Provider system (provide/inject)

Runtime state is managed through typed providers rather than loose callable injection on `Duel`.

Each concern defines a `runtime.py` module containing a plain class that encapsulates the concern's mutable state and methods:

- `PlayerRuntime` — players, current player, opponent lookup
- `PhaseRuntime` — current phase
- `TurnRuntime` — current turn count
- `SummonRuntime` — normal summon usage tracking
- `ForbidRuntime` — active forbids, checked `do(...)` entrypoint
- `ViewRuntime` — observe implementation

`Duel` holds a `ProviderRegistry` (typed `dict[type, object]` with `provide()`/`inject()` methods). Concern listeners create and `provide()` their runtime objects during `SetPlayers` or `DuelInit`. Other listeners and `Duel` methods access concern state through `duel.inject(XyzRuntime)`.

`Duel.do()` and `Duel.observe()` are authored methods on `Duel` that delegate to `ForbidRuntime` and `ViewRuntime` respectively. Backward-compatible `get_*` accessor methods on `Duel` delegate to the appropriate provider.

### Execution semantics

The execution model has two tiers:

- `emit(...)` is raw dispatcher emission with no forbid check.
- `do(...)` is the public action entrypoint (authored on `Duel`, delegated to `ForbidRuntime`) that performs forbid checks before delegating to `emit(...)`.

Semantic actions (`Draw`, `NormalSummon`, `Attack`) are listener-handled. Each semantic listener plans atomic children and emits a `MultiAction`. A dedicated `@listen(MultiAction)` in `duel/listeners.py` iterates children and emits each through the bus, then emits `CompletedAffair` for the composite. This makes atomic-level operations (`MoveCard`, `LpVary`) visible on the bus and preserves a single authoritative execution path.

### Composition structure

Plugin composition is loaded from `[tool.affairon.profiles.duel]` in `pyproject.toml`.

There is no separate `plugins/` package and no separate `duel-runtime` profile.
Concern listeners are composed directly from their owning packages.

`PYPROJECT_PATH` is resolved by walking upward from the bootstrap module until `pyproject.toml` is found.

Cross-concern Pydantic rebuild ownership is still orchestrated from `mr2020.duel.bootstrap`, but each concern contributes its own rebuild hook.

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
3. `SetPlayers` is emitted first. `PlayerRuntime` is provided.
4. `DuelInit` is emitted next. Concern listeners provide `PhaseRuntime`, `TurnRuntime`, `SummonRuntime`, `ForbidRuntime`, `ViewRuntime`.
5. Runtime card normalization runs.
6. Opening draws happen.
7. Initial life points are assigned by `life_point/`.
8. First-turn draw and first-turn battle entry are forbidden through `Forbid`.
9. `available_actions()` collects concern-contributed actions for the current duel state.
10. `do(action)` delegates to `ForbidRuntime`, which checks forbid policy and then delegates to `emit(action)`.
11. Semantic listeners plan atomic children into `MultiAction`, which is emitted and executed through the bus.
12. Completed work is surfaced through `CompletedAffair` at both atomic and composite levels.

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
- `mr2020/life_points/`, `mr2020/move/`, `mr2020/models/` as concern directories
- `battle/` owning LP mutation and LP initialization
- `Duel.do(...)` implemented directly in `duel/models.py` as an authored method with inline logic
- `Duel` directly owning players/current player/turn/phase/summon/forbid/view fields as its authored shape
- Loose `Callable` injection of helper methods onto `Duel` by listeners
- Direct applier function calls (`apply_move_card()`, `apply_lp_vary()`) bypassing the event bus inside `MultiAction` execution

## Open questions

1. Should rebuild orchestration stay in `duel/bootstrap.py`, or should concern modules eventually self-register more of that startup wiring?
2. Should shared predicates still live in `timing/`, or should some move into duel-loop or concern-local modules as the rule graph grows?
