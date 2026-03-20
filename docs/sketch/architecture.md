# duel-master architecture sketch

## Current status

- We intentionally restarted from a clean scaffold on `dev`.
- The rejected implementation is preserved on `archive/current-impl`.
- This document is now the canonical working draft for architecture discussion.

## Agreed constraints

1. The repository is an umbrella project named `duel_master`; `duel_core` is the first planned engine subproject.
2. Runtime seams should be expressed through typed `affairon` affairs.
3. Planning starts from authoritative Master Rule analysis before full duel-state modeling.
4. Kernel-like execution code must not own authored card semantics.
5. Architecture must be validated through smoke-test-sized executable slices, not large speculative builds.
6. Unsupported areas should fail fast for now; no defensive programming at this stage.
7. Every discussion must be persisted under `docs/sketch/` before implementation moves on.
8. New representations must be derived from an explicit duel progression walk. If a duel step does not force a representation, do not add it.

## Planning status classes

- **Grounded**: directly forced by the currently traced duel progression.
- **Provisional**: plausible, but not yet forced by the traced duel progression.
- **Superseded**: earlier planning text that should no longer be treated as authoritative.

## Recommended implementation direction

### Grounded current method

- Start from one explicit duel progression narrative.
- For each step, record only:
  - what must already be true
  - what happens
  - what changes
- Only introduce a new representation when one of those three cannot be expressed clearly.

### Grounded current anchor flow

Current anchor flow:

1. duel is initialized
2. MR2020 emits opening draws for both players
3. MR2020 emits a forbid against the first `turn_draw`
4. MR2020 emits a forbid against first-turn battle entry
5. entering `Draw` emits a requested `Draw` for the current player
6. if the request is not forbidden, one card is drawn
7. available actions advance through `Standby`, `Main Phase 1`, optional `Battle`, `Main Phase 2`, and `End`
8. first-turn battle entry is modeled by `Forbid`
9. in `Main Phase 1`, the current player may perform one minimal `NormalSummon` into an empty monster zone
10. entering `End` triggers `TurnCleanup`, switches to the next player, and emits the next `EnterPhase(Draw)`
11. on turn 2, a summoned monster may enter `Battle` and attack one opposing monster
12. battle resolution destroys losing monsters, updates LP, records a minimal completion result, and returns to the same action loop

This is the grounded flow for the current slice.

### Grounded current minimums

- `Duel`
- `Player`
- `Phase`
- `DuelInit`
- `EnterPhase`
- `ExitPhase`
- `Draw`
- `NormalSummon`
- `Attack`
- `Forbid`
- `TurnCleanup`
- one current actor
- one current turn counter
- one minimal per-player monster-zone occupancy model
- one turn-scoped normal-summon-used flag
- one minimal per-player graveyard
- one minimal per-player LP total
- one turn-scoped attacked-zone tracker
- baseline turn phases:
  - `Draw`
  - `Standby`
  - `Main Phase 1`
  - `Battle`
  - `Main Phase 2`
  - `End`

### Grounded process rule

Every new representation added from now on must answer:

1. which exact duel step forced it?
2. what could not be expressed without it?
3. why is a simpler concrete description insufficient?

If these questions are not answered, the representation should not be added.

### Reviewed callable usage boundary

The first implementation may begin against the following narrowed boundary:

- Public usage remains call-style through `Duel`.
- `Duel` is constructed from two `Player` objects.
- Each `Player` currently carries two concrete deck instances:
  - main deck
  - extra deck
- Validation remains intentionally minimal for now.

- `Duel` stays concrete and inspectable.
- Public usage remains call-style through `Duel`.
- The current implementation now follows a smaller duel-bound affair flow centered on:
  - `DuelInit`
  - `EnterPhase`
  - `ExitPhase`
  - `Draw`
  - `Forbid`
  - `TurnCleanup`
- Public usage is now centered on:
  - `observe(view=...)`
  - `available_actions()`
  - `do(action)`
  - `emit(affair)`
- `available_actions()` now asks the dispatcher through a dedicated `AvailableActions` affair and only returns listener-contributed actions.
- Current code now returns collected `ExecutableAffair` instances directly.
- `observe(view=...)` should return view-layer data with access control. Public-facing view state must not expose the opponent's private hand or deck data by convenience.

- CLI reads `Duel.observe(...)` for renderable facts.
- Player-specific presentation data should stay on player-facing view objects rather than being flattened into `PublicView`.
- Available user-side progression is surfaced through `available_actions()` for the current actor only.
- User choice flows through `do(action)`.
- Internal rule semantics still flow through emitted affairs, not direct rule branches on `Duel`.
- Public turn progression now reaches the next actor through `EnterPhase(END) -> TurnCleanup -> EnterPhase(DRAW)`.
- Actionable in-game affairs now carry `requester`, and `Forbid` now stores the
  concrete forbidden action affair rather than only a requester callable.
- Phase progression within a turn is currently modeled through `available_actions()` rather than a broader chance/priority system.
- The first field state is now forced by the narrated normal summon step in `Main Phase 1`.

- On user action submission, `Duel.do(...)` emits `ExecutionRequest` for the
  chosen `ExecutableAffair` into the duel-bound dispatcher.
- `Kernel` now owns runtime `State` for the current slice and emits
  `CompletedAffair` after execution finishes.
- Raw runtime access now goes through `Duel.state`.
- The previous convenience proxies on `Duel` for `players`, `current_player`,
  `current_turn`, and `phase` have been removed in favor of explicit state
  access.
- Contradiction resolution and allow/forbid precedence remain expansion targets, not grounded first-slice behavior.
- Downstream timing ownership remains provisional until a narrated trigger/timing case forces that decision.

- Master rules are currently expressed in the smaller MR2020 form forced by this
  slice: named rule callbacks that emit `Draw` and `Forbid` affairs.
- `Duel.setup()` is now the explicit semantic setup step for the current slice.
- `Duel.__init__()` still calls `setup()` to preserve current public behavior.
- Rule setup is now composed from `[tool.affairon]` in `pyproject.toml` rather
  than hardwired as a direct setup call in `Duel`.

### Accepted next direction

The following direction is accepted. Most of it is now implemented in the
current slice.

- Rule setup should be config-driven through `affairon` plugin composition from
  `[tool.affairon]`, not by hardwiring rule setup calls in `Duel`.
- `Duel` remains the public facade and composition root, but setup should stay
  an explicit semantic step rather than disappearing into constructor wiring.
- The current `Action` wrapper is no longer the intended execution model.
- The shared execution-facing base should be `ExecutableAffair`, which remains a
  duel-bound actionable affair.
- `MultiAffair` is one concrete `ExecutableAffair` used for ordered composition
  of multiple child affairs.
- `Forbid` remains an affair, but not part of the execution-facing
  `ExecutableAffair` layer.
- `available_actions()` stays query-only: it emits a collector affair, rules and
  effects contribute executable affairs, and the collected executable affairs
  are returned to the caller.
- `Duel.do(...)` should accept any `ExecutableAffair`, emit an execution request
  for it into the dispatcher, and stop there.
- `Kernel` should own the internal runtime `State`, including concrete gameplay
  objects such as players, current player, current turn, and future field state.
- `Duel` should expose query access over `State`, not own writable runtime data
  directly.
- `Kernel` should own three responsibilities for executable affairs:
  1. resolve contradiction and priority conflicts
  2. interpret executable affairs into concrete execution steps
  3. emit `CompletedAffair(affair: ExecutableAffair)` after execution finishes
- Once a `CompletedAffair` is emitted, newly available trigger windows return to
  the same `available_actions()` collection seam, forming a closed loop.
- Battle-side outcomes should be expressed through concrete child affairs
  (for example card movement and LP variation), not by ad-hoc payload fields
  attached to `CompletedAffair`.
- `Forbid` should target a concrete actionable affair instance, with affair
  equality responsible for distinguishing rule-relevant identity such as
  requester and transition edge.
- `MultiAffair` should remain opaque during conflict-resolution checks for the
  same reason: source identity matters before actual execution.
- `MultiAffair` should only be expanded into ordered child affairs at the actual
  execution stage owned by `Kernel`.
- The validation strategy for this phase is intentionally narrow: maintain one
  smoke flow that proves available-action collection and user-driven duel
  progression still behave as expected.
- The current branch favors pushing the model forward first, then revisiting
  refactors only after the modeled slice reveals where pressure actually forms.

### Provisional notes

- The following are provisional and not yet authoritative:
  - richer effect IR beyond direct `Draw`
  - the exact request-affair name used by `Duel.do(...)` to submit an
    `ExecutableAffair` into the dispatcher
- richer effect IR beyond direct `Draw`
- broader action availability semantics beyond one current actor
- generalized phase graph beyond `DRAW` and `END`

### Superseded notes

- Earlier abstraction-first descriptions should be treated as superseded where they conflict with the progression-first method.
- The previous `DuelRuntime` / effect-compiler / plugin-loading slice is superseded for the current branch of implementation discussion.
- Decision `0010` should now be read as historical only; the next direction is a
  `Kernel`-owned `State`, not a return to the earlier `DuelRuntime` shape.

## Open questions

1. What is the first narrated executable path that forces `ExecutableAffair`
   beyond the current action wrapper?
2. What is the smallest trigger-window case that forces the first practical
   result-affair flow under one executable action?
3. Which exact duel step first forces concrete field state into `State`?

## Next implementation proposal

The recommended next step is to keep the slice small while shifting the
execution model and runtime ownership in a way that matches the accepted next
direction above.

### Next planning move

The next planning move should be a narrated executable walk that covers:

1. collection of executable affairs through `available_actions()`
2. submission through `Duel.do(...)`
3. Kernel conflict resolution and execution
4. emission of `CompletedAffair`
5. re-entry into the next `available_actions()` window

New abstractions should only be introduced where that walk breaks.
