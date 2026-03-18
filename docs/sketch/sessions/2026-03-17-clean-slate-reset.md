# Session note: clean-slate reset

Date: 2026-03-17
Branch: `dev`

## What was decided

- Preserve the rejected implementation on `archive/current-impl`.
- Continue all fresh work from `dev`.
- Reinitialize the project as `duel-master`.
- Use Python 3.12.
- Keep `pydantic` and local `affairon` as runtime dependencies.
- Keep `pytest`, `ruff`, and `basedpyright` as development tools.
- Persist all future discussion in `docs/sketch/architecture.md`, `docs/sketch/sessions/`, and `docs/sketch/decisions/`.

## Why the reset happened

The previous implementation diverged from the agreed architecture after context was fragmented across agents. The reset is meant to restore a clean baseline and force future decisions to be durable and reviewable.

## Recommended next discussion

- Define the minimum canonical runtime model.
- Define the first `affairon` seams.
- Pick the first executable validation slice.

## Initial implementation recommendation captured this session

- Start with canonical state only.
- Add typed runtime seams before any card-local authored semantics.
- Make the first executable validation loop a turn/phase/draw/pass flow.
- Delay card showcase scenarios until the seam shape is stable.

## Follow-up planning update

- `duel_master` is now treated as the umbrella project name.
- `duel_core` is the first planned engine subproject.
- Planning should begin from authoritative OCG Master Rule 2020 materials, not from a full duel model draft.
- Current stage policy is fail-fast and smoke-test-only.
- Official OCG Master Rule 2020 materials were mirrored into `docs/references/yugioh_ocg/`.
