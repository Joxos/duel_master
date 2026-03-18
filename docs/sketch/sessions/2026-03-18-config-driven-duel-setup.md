# Session note: config-driven duel setup

Date: 2026-03-18
Branch: `dev`

## Trigger

After finishing the executable-affair step, the next requested step was to stop
hardwiring MR2020 setup in `Duel` and switch setup to config-driven affairon
composition while keeping `Duel` as the public composition root.

## Scope kept for this step

This step intentionally included:

- adding explicit `Duel.setup()`
- preserving constructor behavior by having `__init__()` call `setup()`
- replacing the hardwired MR2020 setup call with affairon composition from
  `pyproject.toml`

This step intentionally did not include:

- changing MR2020 rule semantics
- changing the public CLI flow
- changing executable-affair semantics from the previous step

## Implemented changes

- removed the direct MR2020 setup import from `duel_core.duel`
- added `Duel.setup()` as the explicit semantic setup step
- made `Duel.setup()` call `PluginComposer(self.dispatcher).compose_from_pyproject(...)`
- kept `__init__()` behavior compatible by calling `self.setup()` after kernel
  registration
- added fail-fast protection against calling `setup()` twice

## Current setup boundary

- `Duel` remains the public facade and composition root
- affairon composition is explicit and host-driven
- local plugins are still declared in `pyproject.toml` under `[tool.affairon]`
- MR2020 registration now comes from that config path rather than a direct call

## Verification

- added focused setup tests
- `uv run pytest tests`
- `uv run ruff check src tests`
- `uv run basedpyright src tests`

All passed.
