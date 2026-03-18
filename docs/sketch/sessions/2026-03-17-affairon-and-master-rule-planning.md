# Session note: affairon and Master Rule first planning

Date: 2026-03-17
Branch: `dev`

## What was established

- `duel_master` is the umbrella project name.
- `duel_core` is the first planned engine subproject.
- Planning should start from authoritative OCG Master Rule 2020 sources before full duel-state modeling.
- Current stage policy is fail-fast, smoke-test-only, and affairon-first.

## Affairon understanding captured this session

- Affairon is not just an event bus.
- It treats typed affairs as requirement seams.
- Multiple callbacks collaborate on the same seam and return merged dict results.
- Mutable affairs allow in-place mutation of explicitly shared runtime objects.
- Ordering is explicit through `after`, not implicit through registration order.
- Plugin composition is a first-class concept through entry points and local plugins.

## Planning consequence for duel_master

- We should use affairon to define typed seams such as:
  - observe current facts
  - ask what is legal now
  - submit primitive outcomes
- We should not treat affairon as a generic callback dumping ground.
- We should not multiply seams early; only the first smoke path should shape the first seams.

## Official references mirrored this session

- `docs/references/yugioh_ocg/masterrule2020_overview.html`
- `docs/references/yugioh_ocg/rulebook_masterrule20200401_ver1.0.pdf`
- `docs/references/yugioh_ocg/INDEX.md`

## Next planning target

- Extract the minimum Master Rule glossary for the first smoke path.
