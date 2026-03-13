# rules

The `rules` package hosts the unified Rule IR layer.

Master Rules and card-authored rules should be modeled here as equal rule
objects. The distinction is source and lifetime, not representation shape.

## MUST DO

- Represent MR2020 defaults and card effects through the same rule vocabulary.
- Express legality, prohibitions, grants, replacements, triggers, modifiers,
  and procedure insertions in rule form.
- Lower author-facing card definitions into runtime rule objects.
- Keep examples grounded in real Yu-Gi-Oh interactions.

## MUST NOT DO

- Must not split protocol rules and card rules into unrelated systems.
- Must not bypass substrate dispatch just because a case feels "core".
- Must not mutate duel state directly without going through kernel primitives.
- Must not expose reducer/query/procedure internals to card authors.

## Validation Heuristic

If a card can say it, the base game should also be able to say it with the same
rule shape whenever possible.
