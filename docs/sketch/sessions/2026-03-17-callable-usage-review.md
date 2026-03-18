# Session note: callable usage review

Date: 2026-03-17
Branch: `dev`

## User proposal reviewed

The user proposed a callable `duel_core` usage model centered on `Duel`, with:

- `Duel` initialized from two `Player` objects
- each `Player` carrying main deck and extra deck instances
- CLI rendering by directly inspecting `Duel`
- CLI looping over `Duel.get_actions`
- action submission flowing back into `Duel`
- `Kernel` listening internally and applying final mutation

## Review outcome

The proposal is close and can support implementation if its ownership boundaries are narrowed.

## Narrowed boundary

- Public API remains call-style on `Duel`.
- `Duel` stays concrete and inspectable.
- Internal affairon ownership belongs to a duel-bound runtime/orchestrator created inside the duel-facing object graph.
- `Duel.get_actions` should first read concrete state and only use collaborative seams where rule cooperation is needed.
- Returned actions must already be contextual for the current duel state.
- `Kernel` is narrowed to concrete mutation plus contradiction / allow-forbid handling.
- Master rules and initial card effects are registered into the internal duel-bound runtime/dispatcher, not directly into `Duel` as effect logic.

## Implementation readiness

With those boundary corrections, implementation may begin.
