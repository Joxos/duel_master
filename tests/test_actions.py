from dataclasses import FrozenInstanceError

import pytest

from duel_engine.actions import (
    Action,
    ActionError,
    ActionType,
    IllegalTargetError,
    InsufficientResourcesError,
    InvalidActionError,
    InvalidPhaseError,
    WrongPlayerError,
    legal_actions,
)
from duel_engine.models import GameState, Player


def test_action_roundtrip_dict_serialization():
    action = Action(
        player_id="p1",
        action_type=ActionType.ACTIVATE_SPELL,
        targets=("card_abc", "SZ_0"),
        cost_info={"lp": 800, "discard": True, "note": "quick effect"},
    )

    payload = action.to_dict()
    restored = Action.from_dict(payload)

    assert restored == action


def test_action_is_frozen_dataclass():
    action = Action(player_id="p1", action_type=ActionType.PASS_PRIORITY)

    with pytest.raises(FrozenInstanceError):
        action.player_id = "p2"


def test_error_hierarchy_is_specific_and_structured():
    for exc in (
        InvalidActionError("invalid action"),
        InvalidPhaseError("invalid phase"),
        IllegalTargetError("illegal target"),
        InsufficientResourcesError("not enough resources"),
        WrongPlayerError("wrong player"),
    ):
        assert isinstance(exc, ActionError)
        assert isinstance(exc, Exception)
        assert str(exc)


def test_legal_actions_for_main_phase_priority_player():
    state = GameState(
        players=(Player(id="p1"), Player(id="p2")),
        phase="MAIN1",
        priority_player="p1",
    )

    actions = legal_actions(state, "p1")
    action_types = {a.action_type for a in actions}

    assert ActionType.NORMAL_SUMMON in action_types
    assert ActionType.SET_MONSTER in action_types
    assert ActionType.ACTIVATE_SPELL in action_types
    assert ActionType.ACTIVATE_TRAP in action_types
    assert ActionType.PASS_PRIORITY in action_types


def test_legal_actions_empty_for_non_priority_player():
    state = GameState(
        players=(Player(id="p1"), Player(id="p2")),
        phase="MAIN1",
        priority_player="p1",
    )

    assert legal_actions(state, "p2") == []


def test_legal_actions_empty_for_unknown_player():
    state = GameState(players=(Player(id="p1"), Player(id="p2")), phase="DRAW")

    assert legal_actions(state, "p3") == []


def test_legal_actions_phase_mapping_supports_battle_and_end():
    battle_state = GameState(
        players=(Player(id="p1"), Player(id="p2")),
        phase="BATTLE",
        priority_player="p1",
    )
    end_state = GameState(
        players=(Player(id="p1"), Player(id="p2")),
        phase="END",
        priority_player="p1",
    )

    battle_types = {a.action_type for a in legal_actions(battle_state, "p1")}
    end_types = {a.action_type for a in legal_actions(end_state, "p1")}

    assert battle_types == {ActionType.DECLARE_ATTACK, ActionType.PASS_PRIORITY}
    assert end_types == {ActionType.END_PHASE, ActionType.PASS_PRIORITY}
