from __future__ import annotations

from dataclasses import replace
from typing import Any

from duel_engine import __version__
from duel_engine.actions import Action, ActionType, InvalidActionError, legal_actions
from duel_engine.models import Card, GameState, Player
from duel_engine.replay import Replay, ReplayData
from duel_engine.rng import RNG, final_state_hash

_PHASE_ORDER = ("DRAW", "STANDBY", "MAIN1", "BATTLE", "MAIN2", "END")


def _turn_player_id(state: GameState) -> str:
    return state.players[(state.turn - 1) % 2].id


def _next_phase(current_phase: str) -> str:
    idx = _PHASE_ORDER.index(current_phase)
    return _PHASE_ORDER[(idx + 1) % len(_PHASE_ORDER)]


def _default_deck(owner_id: str, deck_size: int) -> list[Card]:
    return [
        Card(name=f"{owner_id}_card_{i}", card_type="MONSTER", owner_id=owner_id, face_up=False)
        for i in range(deck_size)
    ]


def init_duel(
    *,
    seed: int,
    deck_size: int = 40,
    hand_size: int = 5,
    p1_deck: list[Card] | None = None,
    p2_deck: list[Card] | None = None,
) -> GameState:
    p1_id = "p1"
    p2_id = "p2"

    p1_cards = (
        p1_deck if p1_deck is not None else _default_deck(owner_id=p1_id, deck_size=deck_size)
    )
    p2_cards = (
        p2_deck if p2_deck is not None else _default_deck(owner_id=p2_id, deck_size=deck_size)
    )

    rng = RNG(seed)
    p1_draw_pile = list(p1_cards)
    p2_draw_pile = list(p2_cards)
    rng.shuffle(p1_draw_pile)
    rng.shuffle(p2_draw_pile)

    return GameState(
        players=(
            Player(
                id=p1_id, hand=tuple(p1_draw_pile[:hand_size]), deck=tuple(p1_draw_pile[hand_size:])
            ),
            Player(
                id=p2_id, hand=tuple(p2_draw_pile[:hand_size]), deck=tuple(p2_draw_pile[hand_size:])
            ),
        ),
        turn=1,
        phase="DRAW",
        step="OPEN",
        priority_player=p1_id,
    )


def step(state: GameState, action: Action) -> GameState:
    available = {candidate.action_type for candidate in legal_actions(state, action.player_id)}
    if action.action_type not in available:
        raise InvalidActionError(f"Illegal action for current state: {action.action_type.value}")

    if action.action_type in (
        ActionType.PASS_PRIORITY,
        ActionType.DRAW_PHASE,
        ActionType.STANDBY_PHASE,
        ActionType.END_PHASE,
    ):
        next_phase = _next_phase(state.phase)
        if state.phase == "END" and next_phase == "DRAW":
            next_turn = state.turn + 1
            next_priority = state.players[(next_turn - 1) % 2].id
            return replace(
                state,
                turn=next_turn,
                phase="DRAW",
                step="OPEN",
                priority_player=next_priority,
            )
        return replace(
            state,
            phase=next_phase,
            step="OPEN",
            priority_player=_turn_player_id(state),
        )

    return state


def run_duel(
    *, seed: int, steps: int = 50, policy: str = "deterministic-default"
) -> tuple[GameState, Replay]:
    state = init_duel(seed=seed)
    initial_hash = final_state_hash(state.to_dict())
    actions_log: list[dict[str, Any]] = []
    choices_log: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = [
        {"type": "initial_state", "state": state.to_dict(), "state_hash": initial_hash}
    ]

    for step_index in range(steps):
        player_id = _turn_player_id(state)
        actions = legal_actions(state, player_id)
        if not actions:
            break

        if policy == "deterministic-default":
            action = next(
                (a for a in actions if a.action_type == ActionType.PASS_PRIORITY), actions[0]
            )
        else:
            raise ValueError("Only deterministic-default is supported by run_duel")

        actions_log.append({"step": step_index, **action.to_dict()})
        choices_log.append(
            {
                "step": step_index,
                "policy": policy,
                "request": "select_action",
                "choice": action.action_type.value,
            }
        )
        state = step(state, action)
        events.append(
            {
                "type": "state_after_action",
                "step": step_index,
                "state_hash": final_state_hash(state.to_dict()),
                "turn": state.turn,
                "phase": state.phase,
            }
        )

    final_hash = final_state_hash(state.to_dict())
    events.append({"type": "final_state_hash", "state_hash": final_hash})

    replay = Replay(
        data=ReplayData(
            engine_version=__version__,
            ruleset_id="MR2020",
            seed=seed,
            initial_state_hash=initial_hash,
            actions=actions_log,
            choices=choices_log,
            events=events,
        )
    )

    return state, replay
