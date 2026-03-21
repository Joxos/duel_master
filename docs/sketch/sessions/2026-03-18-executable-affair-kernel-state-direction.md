# Session note: executable affair and kernel-owned state direction

Date: 2026-03-18
Branch: `dev`

## Trigger

The user clarified the intended next direction for the current duel slice and
asked that it be recorded under `docs/`.

The main points were:

- setup should be config-driven rather than hardwired
- `Duel` may remain the public composition root
- setup behavior should become explicit semantic flow rather than inline
  constructor emissions
- the current `Action` wrapper should be replaced by an execution-facing affair
  model
- `Kernel` should own runtime state and execution responsibility
- conflict resolution, execution completion, and trigger reopening should form a
  closed loop
- forbid targeting should remain callable-identity-based
- the current testing strategy should stay minimal and smoke-oriented

## Reviewed prior authority

Before recording the new direction, the following records were reviewed:

- `docs/sketch/architecture.md`
- `docs/sketch/decisions/0005-affair-graph-is-listener-driven.md`
- `docs/sketch/decisions/0008-kernel-owns-final-resolution-and-downstream-timing.md`
- `docs/sketch/decisions/0010-duelruntime-owned-by-kernel.md`
- `docs/sketch/decisions/0011-minimal-duelinit-draw-slice.md`
- `docs/sketch/sessions/2026-03-18-duelruntime-kernel-setup-refactor.md`
- `docs/sketch/sessions/2026-03-18-dispatcher-available-actions-requester-inheritance.md`
- current code in `src/duel_core/`

## Current executable facts

The currently running slice still behaves as follows:

- `available_actions()` emits `AvailableActions` and returns collected
  `Action(label, actor, affair)` wrappers
- `Duel.do(...)` validates the selected wrapper and emits its underlying affair
- visible runtime state still lives directly on `Duel`
- `Kernel` currently owns forbid bookkeeping and concrete mutation listeners
- MR2020 rule setup is still hardwired in `Duel.__init__()` even though
  `pyproject.toml` already declares `duel_core.mr2020:setup` as a local affairon
  plugin

These facts remain the current executable slice. The points below describe the
accepted next direction, not a claim about current implementation.

## Direction recorded

### Setup and host composition

- Rule setup should be config-driven through `[tool.affairon]` plugin
  composition.
- `Duel` may remain the public facade and composition root.
- The setup phase should become explicit semantic flow instead of being hidden
  as constructor-only wiring.

### Execution-facing affair model

- The current `Action` wrapper is not the intended long-term model.
- The shared execution-facing base should be named `ExecutableAffair`.
- `ExecutableAffair` remains a duel-bound actionable affair.
- `MultiAffair` is one concrete `ExecutableAffair` used to group multiple child
  affairs in order.
- `Forbid` remains an affair, but not part of the `ExecutableAffair` layer.

### Action collection

- `available_actions()` remains query-only.
- It asks the dispatcher for currently available executable affairs.
- Rules, effects, and other semantic listeners contribute those executable
  affairs.
- The collected executable affairs are returned upward without `Duel` deciding
  semantic validity itself.

### Submission and execution ownership

- `Duel.do(...)` should accept any `ExecutableAffair`.
- `Duel.do(...)` should submit an execution request for that executable affair
  into the dispatcher and stop there.
- After submission, `Kernel` becomes the execution owner.

### Kernel-owned runtime state

- `Kernel` should own an internal runtime `State` object.
- `State` should contain concrete gameplay objects and mutable runtime facts,
  including players, current player, current turn, and future field state.
- `Duel` should expose queries over that state rather than keep writable runtime
  state as its own public surface.

### Kernel responsibilities

For the next direction, `Kernel` should own:

1. contradiction and priority resolution between competing effects
2. coordination of planner and applier collaborators for concrete execution steps
3. emission of `CompletedAffair(action: ExecutableAffair, result: DuelAffair)` once execution
   finishes

### Closed loop after completion

- `CompletedAffair` exists to reopen downstream trigger timing.
- Once new triggers or effects become available, the flow returns to the same
  `available_actions()` collection seam.
- This keeps user choice, execution, completion, and newly available responses
  in one loop.

### Forbid targeting rule

- `Forbid.target` should continue to point at a specific callable identity.
- The purpose is source distinction, not affair-type distinction.
- Different effects may emit the same affair type while still needing separate
  forbid behavior because they originate from different functions.

### MultiAffair handling rule

- `Duel.do(...)` should treat `MultiAffair` the same way as any other
  executable affair: submit it unchanged.
- During conflict resolution, `Kernel` should also treat `MultiAffair` as one
  executable affair so source identity is preserved.
- Only at actual execution time should `Kernel` expand `MultiAffair` into its
  ordered child affairs and emit them in sequence.

## Conflict reconciliation recorded here

- The earlier `DuelRuntime` record in `0010` no longer matches either current
  code or the newly accepted direction.
- The next direction keeps Kernel-owned runtime state, but records it as a
  `State` model rather than reviving the earlier `DuelRuntime` shape.
- The current code path still hardwires MR2020 setup. The accepted direction is
  to move back to config-driven composition through affairon.

## Testing stance for this phase

- The user explicitly wants a narrow testing strategy during rapid iteration.
- For now the maintained test target is one smoke flow.
- That smoke flow should prove that available executable affairs are returned
  and that user choice can still advance duel progression as expected.

## Result

- The next execution model is now documented as `ExecutableAffair`-centered.
- Kernel-owned state is now documented as the intended next runtime boundary.
- Callable-identity forbids remain the accepted near-term rule.
- The architecture draft and decisions should now be aligned around this
  direction rather than the older `DuelRuntime` record.
