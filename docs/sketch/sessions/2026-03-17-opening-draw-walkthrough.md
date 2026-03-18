# Session note: opening draw walkthrough

Date: 2026-03-17
Branch: `dev`

## Scope of this walkthrough

This walkthrough starts after duel setup is already complete. That is the
smallest truthful entrypoint for the first traced flow.

It does not yet describe shuffle, opening hand draw, or deciding the opening
player. Those belong to an earlier walk.

## Walkthrough

### Step 1

#### What must already be true

- a duel exists
- two players exist in the duel
- duel setup is complete
- one player is the current turn owner
- the duel is currently in Draw phase
- there is some concrete way to tell that this is the opening player's skipped draw

#### What happens

- runtime reads the current concrete duel state
- runtime determines that the current draw step is skipped

#### What changes

- nothing changes yet

### Step 2

#### What must already be true

- the draw step is known to be skipped

#### What happens

- runtime determines the one legal next action in this traced flow
- that action is to advance to the next phase

#### What changes

- the next legal action becomes known to runtime

### Step 3

#### What must already be true

- one legal action has been identified

#### What happens

- that action is applied if legal

#### What changes

- phase changes from Draw to Standby
- turn owner stays the same

### Step 4

#### What must already be true

- phase advancement has already been applied

#### What happens

- runtime reads the updated concrete duel state

#### What changes

- runtime now sees `phase = Standby`

## Grounded consequences

- current facts can still be read directly from concrete duel state
- the first traced flow does not yet force card objects, zone objects, or rich effect structures
- the first missing concept is not a card abstraction, but a concrete way to know whether the current draw step is the skipped opening draw

## Still not grounded

- exact affair names
- exact IR names
- placeholder vocabulary beyond what a later walk proves
- whether runtime-to-kernel handoff must already be event-shaped at this first step
