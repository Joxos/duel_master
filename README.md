# duel-master

`dev` is the clean-slate development branch for the next implementation of
`duel-master`.

## Branch policy

- `archive/current-impl`: preserved snapshot of the rejected implementation
- `legacy`: older experimental history
- `main`: clean baseline branch
- `dev`: active branch for fresh development

## Current baseline

This branch intentionally starts from a minimal Python 3.12 scaffold:

- `pydantic` is available for canonical state models
- `affairon` is available for typed runtime seams
- `pytest`, `ruff`, and `basedpyright` are the retained development tools

## Discussion persistence

To avoid context loss, every architecture discussion must be persisted under
`docs/sketch/`:

- `docs/sketch/architecture.md`: current working architecture draft
- `docs/sketch/sessions/`: session-by-session notes
- `docs/sketch/decisions/`: durable decisions and rationale

## Immediate goal

Rebuild from first principles through small executable slices, while keeping the
architecture discussion durable and reviewable.

## TODO

- Revisit semantic-action re-entry through `kernel.do(...)`: semantic forbids correctly target semantic actions, but semantic-to-atomic translation currently still routes through the same execution entrance in a few places and may deserve a narrower handoff boundary later.
