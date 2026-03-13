# duel_engine

This repository is intentionally reset on `main` for a fresh architecture-first
implementation.

## Branch Policy

- `legacy`: previous experimental implementation history
- `main`: clean branch for the new design and development path

## Current State

- Runtime implementation has been cleared from `main`
- New development should proceed from first principles
- Architectural boundaries should be reintroduced deliberately, not by carrying
  over old patches

## Kept on Main

- project tooling (`pyproject.toml`, `uv.lock`, `.gitignore`)
- development constraints (`agents.md`)

## Next Expectation

Rebuild the engine from scenario-driven architecture validation rather than
incrementally patching the previous prototype.
