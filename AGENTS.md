# AGENTS.md

This file is for coding agents working in `/home/Joxos/source/duel_master`.
Use it as repository-specific guidance, not as generic Python advice.

## Scope

- This repo is Python, not JS/TS.
- Python baseline is 3.12+.
- The code uses a `src/` layout.
- The active development branch is `dev`.
- `duel_core` is the active engine slice.
- `duel_master` currently exposes the CLI.

## Read these first

Before changing code, read the sources that define the current slice:

1. `README.md`
2. `agents.md`
3. `pyproject.toml`
4. `docs/sketch/architecture.md`
5. Relevant files in `docs/sketch/decisions/`
6. Relevant recent files in `docs/sketch/sessions/`

The existing lowercase `agents.md` is an authoritative local rules file.
This `AGENTS.md` translates and extends that guidance in English.

## Editor-specific instruction files

At the time this file was written, the repo had:

- no `.cursorrules`
- no `.cursor/rules/`
- no `.github/copilot-instructions.md`

Do not assume hidden editor policy files exist.

## Layout

- `src/duel_core/`: duel engine, affairs, kernel, models, phases, rules slice
- `src/duel_master/`: CLI package and entry point
- `tests/`: pytest suite
- `examples/`: executable examples
- `docs/sketch/architecture.md`: current architecture draft
- `docs/sketch/decisions/`: durable decisions
- `docs/sketch/sessions/`: session notes

## Verified commands

Use `uv run ...` for dev tools.

### Tests

- Full suite: `uv run pytest tests`
- Single test file: `uv run pytest tests/test_smoke.py`
- Single test by name:
  - `uv run pytest tests/test_smoke.py -k test_main_returns_zero`

The same pattern works for focused engine tests, for example:

- `uv run pytest tests/duel_core/test_opening_draw_flow.py`
- `uv run pytest tests/duel_core/test_opening_draw_flow.py -k test_unknown_user_action_is_rejected`

### Lint

- `uv run ruff check src tests`

### Type check

- `uv run basedpyright src tests`

### Build

- `uv build`

`uv build` currently produces both sdist and wheel via the setuptools backend
declared in `pyproject.toml`.

## Tooling facts from config

- Ruff line length: `100`
- Ruff target version: `py312`
- BasedPyright type checking mode: `basic`
- Pytest test root: `tests`
- CLI script entry point: `duel-master = duel_master.cli:main`

## Working style for this branch

This branch is intentionally small and architecture-first.

- Rebuild from first principles through small executable slices.
- Prefer the smallest concrete change that proves the next step.
- Unsupported areas should fail fast for now.
- Do not add speculative abstractions before the duel progression forces them.
- Validate direction with smoke-sized behavior, not a large speculative build.

## Architecture rules that matter

These are explicit in `docs/sketch/architecture.md` and recent decisions:

- Runtime seams should be expressed through typed `affairon` affairs.
- Kernel-like execution code must not own authored card semantics.
- New representations must be forced by an explicit duel progression step.
- Public usage is centered on:
  - `observe(view=...)`
  - `available_actions()`
  - `do(action)`
  - `emit(affair)`
- `available_actions()` is listener-driven.
- Actionable affairs carry `requester` when semantic origin matters.

Prefer extending listener-driven behavior in `mr2020.py` and `kernel.py` before
adding direct logic branches to `Duel`.

## Discussion persistence is mandatory

The repo treats architecture discussion as part of the work.

- Update `docs/sketch/architecture.md` when the working draft changes.
- Add a note under `docs/sketch/sessions/` for each discussion session.
- Record settled outcomes under `docs/sketch/decisions/`.
- Align implementation with those records before extending the slice.

If the design changes and the docs do not, the work is incomplete.

## Code style

### Imports

- Prefer absolute imports from `duel_core` and `duel_master`.
- Separate import groups with a blank line when groups differ.
- Keep imports explicit. Do not use wildcard imports.
- Use `typing` imports sparingly.
- Prefer built-in generics; current code only uses `TYPE_CHECKING` where needed.

### Typing

- Use modern Python 3.12 typing syntax.
- Prefer `list[str]`, `tuple[Player, Player]`, and `Callable[..., object]`.
- Prefer `X | None` over `typing.Optional[X]`.
- Type new functions, helpers, and pytest fixtures.
- Match existing concrete return annotations.

### Models and state

- State models are Pydantic models.
- Follow the existing `BaseModel` + `ConfigDict` pattern.
- Use `Field(default_factory=...)` for mutable defaults.
- Freeze models only when immutability is part of the design.
- Keep fields concrete and easy to inspect.

### Naming and structure

- Modules, variables, functions, and tests use `snake_case`.
- Classes use `PascalCase`.
- Constants use `UPPER_SNAKE_CASE`.
- Test files use `test_*.py`.
- Test names should describe behavior directly.
- Keep functions short and concrete.
- Prefer direct assertions over clever indirection.
- Preserve `__all__` exports when public surface area changes.

### Comments and docstrings

From `agents.md`:

- Full-sentence comments go on their own line and start with a capital letter.
- Incomplete fragments belong in end-of-line comments and start lowercase.
- Module docstrings are optional at this MVP stage.
- Class and function docstrings should use Google style when they add value.
- Do not write empty docstrings that only restate the name.

### Error handling

- Fail fast on invalid domain input.
- Raise clear exceptions, as current code does with `ValueError`.
- Do not add silent fallbacks.
- Do not add defensive layers for unsupported behavior unless the current
  architecture notes now require them.

## Tests and examples

- Keep tests under `tests/`, usually mirroring the affected area under `src/`.
- Use plain pytest function tests.
- Type pytest fixtures when they appear in signatures.
- Match the existing style of small builder helpers like `build_duel()`.
- Keep `examples/` executable.
- Examples should remain callable from smoke-style tests.

## Practical repo-specific patterns

- `Duel` currently expects exactly two `Player` objects.
- The public flow is concrete and inspectable, not hidden behind a large wrapper.
- `AvailableActions` is a collector affair; add actions through listeners.
- Keep CLI behavior aligned with `observe(...)` output and available actions.

## Before you finish

Run the smallest relevant check first, then broaden:

1. Targeted pytest command for the touched file or test name
2. `uv run pytest tests` when shared behavior changed
3. `uv run ruff check src tests`
4. `uv run basedpyright src tests`
5. `uv build` when packaging or entry points changed

If your change alters architecture, also update the matching files under
`docs/sketch/`.
