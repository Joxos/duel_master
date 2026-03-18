# Decision 0010: DuelRuntime is internal and Kernel-owned

Status: superseded
Date: 2026-03-18

## Decision

This note recorded an earlier runtime refactor direction around an internal
`DuelRuntime` object.

It should no longer be treated as current authority.

## Historical direction

The historical direction in this note was:

- concentrate mutable runtime state in `DuelRuntime`
- let `Kernel` own runtime mutation and forbid bookkeeping
- make `setup()` explicit while preserving constructor behavior

## Scope

This note previously claimed that `DuelRuntime` owned:

- `turn_owner`
- `phase`
- `setup_complete`
- `forbids`

and that `Kernel` owned:

- runtime creation
- runtime mutation during applied actions
- explicit runtime phase mutation helpers used by this slice's tests/setup support
- forbid registration
- forbid cleanup when phases exit

## Boundary

This boundary is retained only as historical context.

## Why it is superseded

- Current code no longer matches this shape.
- The architecture draft now treats the older `DuelRuntime` slice as
  superseded.
- The accepted next direction is now recorded in `0012`, which keeps
  Kernel-owned runtime state but models it around `State` and executable
  affairs instead of reviving the earlier `DuelRuntime` boundary.

## Replacement

See instead:

- `docs/sketch/decisions/0011-minimal-duelinit-draw-slice.md`
- `docs/sketch/decisions/0012-executable-affair-kernel-state-direction.md`
- `docs/sketch/architecture.md`
