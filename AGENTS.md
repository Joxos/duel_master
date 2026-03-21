# AGENTS.md

This file is the English working guide for coding agents in `/home/Joxos/source/duel_master`.
The lowercase `agents.md` contains supplementary local rules in Chinese.

## Scope

- Python 3.12+, `src/` layout
- Active branch: `dev`
- Active engine slice: `duel_core`; CLI entry point: `duel_master`

## Read these first

1. `README.md`
2. `agents.md` (local rules)
3. `pyproject.toml`
4. `docs/sketch/architecture.md`
5. Relevant files in `docs/sketch/decisions/`
6. Recent files in `docs/sketch/sessions/`

## Repository layout

| Path | Purpose |
|---|---|
| `src/duel_core/` | Duel engine: affairs, kernel, models, phase logic, rules |
| `src/duel_master/` | CLI package and entry point |
| `tests/` | Pytest suite (currently sparse) |
| `examples/` | Executable example scripts |
| `docs/sketch/architecture.md` | Current working architecture draft |
| `docs/sketch/decisions/` | Settled decisions with rationale |
| `docs/sketch/sessions/` | Session-by-session notes |

## Verified commands

Use `uv run ...` for all development tools.

### Tests

```bash
# Full suite
uv run pytest tests

# Single test file
uv run pytest tests/test_smoke.py

# Single test by name
uv run pytest tests/test_smoke.py -k test_main_returns_zero

# Focused example
uv run pytest tests/duel_core/test_opening_draw_flow.py -k test_unknown_user_action_is_rejected
```

### Lint / type check / build

```bash
uv run ruff check src tests
uv run basedpyright src tests
uv build
```

## Tooling facts

- Ruff: line-length 100, target py312
- BasedPyright: typeCheckingMode "basic"
- Pytest test root: `tests`
- CLI entry point: `duel-master = duel_master.cli:main`
- Affairon plugin: `duel_core.mr2020:setup` (from `[tool.affairon]`)

## Architecture rules

These come from `docs/sketch/architecture.md`:

- Runtime seams: typed `affairon` affairs
- Kernel owns runtime `State`; `Duel` exposes query access via `Duel.state`
- Public API: `observe(view=...)`, `available_actions()`, `do(action)`
- `available_actions()` is listener-driven; returns collected `ExecutableAffair` values
- `Duel.do(...)` accepts an `ExecutableAffair` and submits it to `Kernel.do(...)`
- `Kernel` emits `CompletedAffair` after execution
- Prefer listener-driven behavior in `mr2020.py` and `kernel.py` over direct `Duel` branches
- Actionable affairs carry `requester` when semantic origin matters

## Working style

- Rebuild from first principles through small executable slices
- Prefer the smallest concrete change that proves the next step
- Unsupported areas fail fast; no speculative abstractions
- Validate with smoke-sized behavior, not large speculative builds
- Discussion persistence is mandatory: update `docs/sketch/` after architecture changes

## Code style

### Imports and formatting

- Prefer absolute imports from `duel_core` and `duel_master`
- Separate import groups with a blank line when groups differ
- Keep imports explicit; no wildcard imports
- Use `typing` imports sparingly
- Keep code within Ruff's line length of 100

### Typing

- Use modern Python 3.12 syntax: `list[str]`, `tuple[Player, Player]`
- Prefer `X | None` over `typing.Optional[X]`
- Type all new functions, helpers, and pytest fixtures
- State models: `BaseModel` + `ConfigDict` pattern with `Field(default_factory=...)`
- Keep runtime data on `Kernel` state, not ad hoc fields on `Duel`

### Naming

- Modules, variables, functions, tests: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Test files: `test_*.py`

### Comments and docstrings

- Full-sentence comments on their own line, capitalized
- Incomplete fragments: end-of-line comments, lowercase
- Module docstrings optional at MVP stage
- Class/function docstrings: Google style when they add value
- Do not write docstrings that only restate the name

### Error handling

- Fail fast on invalid domain input
- Raise clear exceptions (e.g., `ValueError`)
- No silent fallbacks or defensive layers for unsupported behavior

## Tests and examples

- Tests under `tests/`, mirroring the affected area under `src/`
- Plain pytest function tests; type fixtures in signatures
- Keep `examples/` executable and callable from smoke tests
- Current test coverage is minimal; expand as slice grows

## Practical patterns

- `Duel` expects exactly two `Player` objects
- `AvailableActions` is a collector affair; add actions through listeners
- Phase progression through `available_actions()`, not a larger timing system
- Blue-Eyes White Dragon exists as reference data; tribute-summon out of scope

## Before you finish

Run checks in order, broadening only as needed:

1. Targeted pytest for the touched file or specific test name
2. `uv run pytest tests` if shared behavior changed
3. `uv run ruff check src tests`
4. `uv run basedpyright src tests`
5. `uv build` if packaging or entry points changed

If your change alters architecture, also update the matching files under `docs/sketch/`.
