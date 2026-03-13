# architecture_validation examples

These examples exist to validate cross-module interactions before a final public
architecture API is locked in.

They are intentionally scenario-driven.

## MUST DO

- Demonstrate concrete Yu-Gi-Oh semantics through small focused scenarios.
- Make layer interaction visible in returned summaries or traces.
- Stay small enough to serve as smoke validation and design discussion input.

## MUST NOT DO

- Must not introduce speculative grand APIs just for elegance.
- Must not hide key rule interactions behind opaque helpers.
- Must not become detached from real card/rule cases.
