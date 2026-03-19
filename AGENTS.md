# AGENTS.md

This file is for coding agents working in `/home/Joxos/source/duel_master`.
Use it as repository-specific guidance, not as generic Python advice.

## Scope

- This repo is Python, not JS/TS.
- Python baseline is 3.12+.
- The code uses a `src/` layout.
- The active development branch is `dev`.
- `duel_core` is the active engine slice.
- `duel_master` currently exposes the CLI entry point.

## Read these first

Before changing code, read these files in order:

1. `README.md`
2. `agents.md`
3. `pyproject.toml`
4. `docs/sketch/architecture.md`
5. Relevant files in `docs/sketch/decisions/`
6. Relevant recent files in `docs/sketch/sessions/`

The lowercase `agents.md` is an authoritative local rules file.
This `AGENTS.md` is the English working guide for agentic coding in this repo.

## Editor-specific instruction files

At the time of writing, this repo has no `.cursorrules`, no `.cursor/rules/`,
and no `.github/copilot-instructions.md`.

## Repository layout

- `src/duel_core/`: duel engine, affairs, kernel, models, phase logic, rules slice
- `src/duel_master/`: CLI package and entry point
- `tests/`: pytest suite
- `examples/`: executable examples and helper scripts
- `docs/sketch/architecture.md`: current architecture draft
- `docs/sketch/decisions/`: durable decisions
- `docs/sketch/sessions/`: session notes

## Verified commands

Use `uv run ...` for development tools.

### Tests

- Full suite: `uv run pytest tests`
- Single test file: `uv run pytest tests/test_smoke.py`
- Single test by name: `uv run pytest tests/test_smoke.py -k test_main_returns_zero`
- Another focused example: `uv run pytest tests/duel_core/test_opening_draw_flow.py`
- Focused by name: `uv run pytest tests/duel_core/test_opening_draw_flow.py -k test_unknown_user_action_is_rejected`

### Lint / type check / build

- `uv run ruff check src tests`
- `uv run basedpyright src tests`
- `uv build`

## Tooling facts from config

- Ruff line length: `100`
- Ruff target version: `py312`
- BasedPyright type checking mode: `basic`
- Pytest test root: `tests`
- CLI entry point: `duel-master = duel_master.cli:main`
- Affairon plugin setup comes from `[tool.affairon]`

## Working style for this branch

This branch is intentionally small and architecture-first.

- Rebuild from first principles through small executable slices.
- Prefer the smallest concrete change that proves the next step.
- Unsupported areas should fail fast for now.
- Do not add speculative abstractions before duel progression forces them.
- Validate direction with smoke-sized behavior, not speculative large builds.

## Architecture rules that matter

These rules come from `docs/sketch/architecture.md` and recent decisions:

- Runtime seams should be expressed through typed `affairon` affairs.
- Kernel-like execution code must not own authored card semantics.
- New representations must be forced by an explicit duel progression step.
- Public usage is centered on `observe(view=...)`, `available_actions()`, `do(action)`, and `emit(affair)`.
- `available_actions()` is listener-driven and returns collected `ExecutableAffair` values.
- `Duel.do(...)` accepts an `ExecutableAffair` and submits execution through the dispatcher.
- `Kernel` owns runtime `State`; `Duel` exposes query access through `Duel.state`.
- Actionable affairs carry `requester` when semantic origin matters.

Prefer extending listener-driven behavior in `mr2020.py` and `kernel.py` before
adding direct logic branches to `Duel`.

## Discussion persistence is mandatory

Architecture discussion is part of the work.

- Update `docs/sketch/architecture.md` when the working draft changes.
- Add a session note under `docs/sketch/sessions/` for each discussion.
- Record settled outcomes under `docs/sketch/decisions/`.
- Align implementation with those records before extending the slice.

If the design changed and the docs did not, the work is incomplete.

## Code style

### Imports and formatting

- Prefer absolute imports from `duel_core` and `duel_master`.
- Separate import groups with a blank line when groups differ.
- Keep imports explicit. Do not use wildcard imports.
- Use `typing` imports sparingly.
- Match the surrounding file's formatting instead of reflowing unrelated code.
- Keep code within Ruff's configured line length of 100.

### Typing and models

- Use modern Python 3.12 typing syntax.
- Prefer built-in generics such as `list[str]` and `tuple[Player, Player]`.
- Prefer `X | None` over `typing.Optional[X]`.
- Type new functions, helpers, and pytest fixtures.
- State models are Pydantic models; follow the current `BaseModel` + `ConfigDict` pattern.
- Use `Field(default_factory=...)` for mutable defaults.
- Keep runtime data on `Kernel` state, not ad hoc fields on `Duel`.

### Naming, comments, and docstrings

- Modules, variables, functions, and tests use `snake_case`.
- Classes use `PascalCase`.
- Constants use `UPPER_SNAKE_CASE`.
- Test files use `test_*.py`, and test names should describe behavior directly.
- Full-sentence comments go on their own line and start with a capital letter.
- Incomplete fragments belong in end-of-line comments and start lowercase.
- Module docstrings are optional at this MVP stage.
- Class and function docstrings should use Google style when they add value.
- Do not write docstrings that only restate the name.

### Error handling

- Fail fast on invalid domain input.
- Raise clear exceptions, as current code already does with `ValueError`.
- Do not add silent fallbacks.
- Do not add defensive layers for unsupported behavior unless architecture notes now require them.

## Tests and examples

- Keep tests under `tests/`, usually mirroring the affected area under `src/`.
- Use plain pytest function tests.
- Type pytest fixtures when they appear in signatures.
- Match the existing style of small builder helpers in test support code.
- Keep `examples/` executable.
- Examples should remain callable from smoke-style tests when practical.

## Practical repo-specific patterns

- `Duel` currently expects exactly two `Player` objects.
- The public flow is concrete and inspectable, not hidden behind a large wrapper.
- `AvailableActions` is a collector affair; add actions through listeners.
- Phase progression is currently modeled through `available_actions()` rather than a larger timing system.
- Keep CLI behavior aligned with `observe(...)` output and available actions.
- Blue-Eyes White Dragon exists as reference/runtime card data, but tribute-summon behavior is still out of scope for the current slice.

## Before you finish

Run the smallest relevant check first, then broaden only as needed:

1. Targeted pytest command for the touched file or specific test name
2. `uv run pytest tests` when shared behavior changed
3. `uv run ruff check src tests`
4. `uv run basedpyright src tests`
5. `uv build` when packaging or entry points changed

If your change alters architecture, also update the matching files under `docs/sketch/`.
