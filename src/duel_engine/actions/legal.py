from __future__ import annotations

from duel_engine.models.state import GameState

from .protocol import Action
from .types import ActionType


def legal_actions(state: GameState, player_id: str) -> list[Action]:
    if state.priority_player and state.priority_player != player_id:
        return []

    if player_id not in (state.players[0].id, state.players[1].id):
        return []

    phase_actions: dict[str, tuple[ActionType, ...]] = {
        "DRAW": (ActionType.DRAW_PHASE, ActionType.PASS_PRIORITY),
        "STANDBY": (ActionType.STANDBY_PHASE, ActionType.PASS_PRIORITY),
        "MAIN1": (
            ActionType.NORMAL_SUMMON,
            ActionType.SET_MONSTER,
            ActionType.ACTIVATE_SPELL,
            ActionType.ACTIVATE_TRAP,
            ActionType.PASS_PRIORITY,
        ),
        "BATTLE": (ActionType.DECLARE_ATTACK, ActionType.PASS_PRIORITY),
        "MAIN2": (
            ActionType.NORMAL_SUMMON,
            ActionType.SET_MONSTER,
            ActionType.ACTIVATE_SPELL,
            ActionType.ACTIVATE_TRAP,
            ActionType.PASS_PRIORITY,
        ),
        "END": (ActionType.END_PHASE, ActionType.PASS_PRIORITY),
    }

    action_types = phase_actions.get(state.phase, (ActionType.PASS_PRIORITY,))
    return [
        Action(player_id=player_id, action_type=action_type)
        for action_type in action_types
    ]
