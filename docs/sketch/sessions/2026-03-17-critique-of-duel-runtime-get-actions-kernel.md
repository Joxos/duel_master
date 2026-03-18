# Session note: critique of Duel, get_actions, and Kernel boundaries

Date: 2026-03-17
Branch: `dev`

## Point 1: separate Runtime object or not

Conclusion:

- A separate public `Runtime` object is not the grounded requirement.
- The real requirement is that affairon collaboration stays duel-bound and out of the raw concrete `Duel` data fields.
- Implementing that as a private internal collaboration layer inside `Duel` is acceptable.

## Point 2: should get_actions broadcast directly

Conclusion:

- The user's push is directionally right, but the boundary needs narrowing.
- If `Duel` should not own authored semantics, then `get_actions` asking the internal affair layer for currently available actions is coherent.
- However, `get_actions` should not be frozen as an unconditional broadcast by default.
- It should read concrete current state first and only open collaboration where the traced flow actually forces rule cooperation.

## Point 3: action values returned to CLI

Conclusion:

- Returned actions should be selectable in the current state.
- If they are represented using effect IR, they must already be contextual enough for user selection.

## Point 4: should Kernel decide final outcomes and downstream timing

Conclusion:

- Yes, with one important narrowing.
- `Kernel` should own final contradiction handling, allow-forbid precedence, and concrete mutation.
- But authored rule semantics should still be contributed from listeners rather than handwritten directly in kernel branches.
- General downstream timing ownership should remain provisional until a narrated trigger/timing case forces it.
