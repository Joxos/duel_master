# cards

The `cards` package hosts card data, card-authored rule bundles, and card
authoring helpers.

It should remain focused on expressing card intent, not runtime machinery.

## MUST DO

- Define card data and card-authored rule bundles cleanly.
- Keep card authoring focused on declarative intent and selectors/operations.
- Provide examples and fixtures for concrete card interactions.
- Preserve traceability back to official text or reference scripts.

## MUST NOT DO

- Must not contain manual event-bus plumbing.
- Must not implement reducer/query/procedure internals.
- Must not perform direct state mutation outside kernel primitives.
- Must not become a dumping ground for hardcoded duel flow patches.

## Borrowing Notes

YGOPro `script/` remains a useful reference for effect bootstrap structure.
Any future Lua-to-DSL tooling should land here or adjacent tooling, not inside
kernel or substrate.
