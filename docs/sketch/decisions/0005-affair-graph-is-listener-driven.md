# Decision 0005: affair graph is runtime-rooted and listener-driven

Status: accepted
Date: 2026-03-17

## Decision

Interaction graphs must describe runtime entrypoints, runtime emission, listener reaction, and kernel mutation. Affairs do not directly operate on other affairs.

## Consequences

- The runtime/orchestrator emits typed affairs.
- Current facts are read directly by runtime from concrete duel state unless a later slice proves an affair is needed.
- Listeners react and return semantics needed downstream.
- `Kernel` listens for action requests and performs concrete duel mutation.
- Graphs should be written as runtime/listener/kernel flow, not as affair-to-affair arrows with implied direct agency.
- Any named affairs beyond this methodological rule remain provisional until the narrated duel walk forces them.
