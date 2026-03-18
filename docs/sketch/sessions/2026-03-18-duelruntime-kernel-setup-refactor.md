# Session note: DuelRuntime / Kernel / setup refactor

Date: 2026-03-18
Branch: `dev`

## Trigger

The user requested a tighter runtime boundary after reviewing the current code:

- no `Duel = object` fallback hack in affair typing
- duel-bound affair classes should inherit the shared `duel` field
- mutable runtime fields should be concentrated in `DuelRuntime`
- `Kernel` should own runtime mutation and forbid storage
- setup flow should be explicit in `setup()` instead of encoded inline in constructor emissions

## Reviewed prior context before editing

The refactor was grounded against:

- `docs/sketch/architecture.md`
- Decision 0007 (callable Duel with internal collaboration)
- Decision 0008 (Kernel owns final mutation path)
- Decision 0009 (first Kernel is permissive)
- the 2026-03-17 callable usage and Duel/Kernel critique session notes

## Implemented changes

### Runtime ownership

- Added internal `DuelRuntime`
- moved mutable runtime state into it:
  - `turn_owner`
  - `phase`
  - `setup_complete`
  - `forbids`

### Kernel ownership

- `Kernel` now creates and mutates the runtime for this slice
- `Kernel` now owns forbid registration and phase-exit forbid cleanup helpers
- direct writable runtime fields were removed from the public `Duel` facade; explicit phase changes now also route through `Kernel`

### Duel facade

- `Duel` remains the public facade
- `Duel` now exposes runtime-backed properties for:
  - `turn_owner`
  - `phase`
  - `setup_complete`
- `Duel.setup()` now performs setup emissions
- `__init__()` still calls `setup()` to preserve current public behavior

### Affair cleanup

- removed the old `Duel = object` fallback hack
- introduced shared duel-bound affair base classes
- concrete affair classes now inherit the `duel` field instead of repeating it

### MR2020 and CLI behavior

- MR2020 behavior remained unchanged for the current slice
- CLI behavior remained unchanged for the current hotseat demo

## Verification

- `pytest tests` passed
- `ruff check src tests` passed
- `basedpyright src tests` passed
- CLI still ran correctly

## Note on forward refs

Removing the `Duel = object` fallback did require restoring a small explicit `model_rebuild()` step so Pydantic can resolve `Duel` forward references at runtime. This was kept because it fixed a real runtime failure without reintroducing the earlier hack.
