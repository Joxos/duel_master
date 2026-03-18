# Decision 0007: callable Duel with internal affair collaboration

Status: accepted
Date: 2026-03-17

## Decision

The first implementation may expose a call-style API directly on `Duel`, while still using a duel-bound internal `affairon` collaboration layer.

The critical boundary is duel-bound ownership of collaboration, not whether a separate public `Runtime` class exists.

## Consequences

- `Duel` may remain the public facade.
- `Duel` may internally own or delegate to a duel-bound dispatcher/collaboration object.
- `Duel.get_actions` may broadcast current duel state through that internal collaboration layer.
- This is acceptable because semantic judgment is still supplied by rule/effect listeners, not by raw `Duel` state inspection alone.
- CLI may inspect `Duel` directly for rendering and call `Duel` methods for progression.
