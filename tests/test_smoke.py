from duel_engine import __version__
from duel_engine import Duel
from duel_engine.actions import Action, ActionType
from examples.architecture_validation.cannot_activate_monster_effects import (
    run_example as run_cannot_activate_monster_effects,
)
from examples.architecture_validation.cannot_draw import run_example as run_cannot_draw
from examples.architecture_validation.borrowing_notes import run_example as run_borrowing_notes
from examples.architecture_validation.cannot_enter_battle_phase import (
    run_example as run_battle_lock,
)
from examples.architecture_validation.cannot_respond_to_activation import (
    run_example as run_no_response,
)
from examples.architecture_validation.continuous_atk_modifier import (
    run_example as run_continuous_atk_modifier,
)
from examples.architecture_validation.default_draw_phase import (
    run_example as run_default_draw_phase,
)
from examples.architecture_validation.destruction_replaced_with_banish import (
    run_example as run_destruction_replaced_with_banish,
)
from examples.basic_single_duel import run_example as run_basic_single_duel
from examples.replay_roundtrip_duel import run_example as run_replay_roundtrip_duel


def test_version_exists():
    """Validate package version export for smoke checks.

    Returns:
        None.
    """
    assert isinstance(__version__, str)
    assert __version__ != ""


def test_example_basic_single_duel_smoke():
    """Validate the basic single duel example can run.

    Returns:
        None.
    """
    summary = run_basic_single_duel()
    assert summary["phase_progression"] == [
        "DRAW",
        "STANDBY",
        "MAIN1",
        "BATTLE",
        "MAIN2",
        "END",
        "DRAW",
    ]
    assert summary["final_turn"] == 2
    assert summary["final_phase"] == "DRAW"
    assert summary["priority_player"] == "p2"


def test_example_replay_roundtrip_smoke():
    """Validate replay example and replay verification flow.

    Returns:
        None.
    """
    summary = run_replay_roundtrip_duel()
    assert summary["verified"] is True


def test_duel_class_smoke():
    """Validate stateful Duel class can drive one-turn progression.

    Returns:
        None.
    """
    duel = Duel.create(seed=5)
    duel.apply_action(Action(player_id=duel.turn_player_id(), action_type=ActionType.DRAW_PHASE))
    duel.apply_action(Action(player_id=duel.turn_player_id(), action_type=ActionType.STANDBY_PHASE))
    duel.apply_action(Action(player_id=duel.turn_player_id(), action_type=ActionType.PASS_PRIORITY))
    duel.apply_action(Action(player_id=duel.turn_player_id(), action_type=ActionType.PASS_PRIORITY))
    duel.apply_action(Action(player_id=duel.turn_player_id(), action_type=ActionType.PASS_PRIORITY))
    duel.apply_action(Action(player_id=duel.turn_player_id(), action_type=ActionType.END_PHASE))

    assert duel.state.turn == 2
    assert duel.state.phase == "DRAW"
    assert duel.state.priority_player == "p2"


def test_architecture_validation_default_draw_phase():
    summary = run_default_draw_phase()
    assert summary["scenario"] == "default_draw_phase"
    assert len(summary["observations"]) == 4


def test_architecture_validation_battle_lock():
    summary = run_battle_lock()
    assert summary["scenario"] == "cannot_enter_battle_phase_this_turn"
    assert summary["decisions"][2]["decision"] == "resolve grant+forbid to forbidden"


def test_architecture_validation_no_response():
    summary = run_no_response()
    assert summary["scenario"] == "cannot_respond_to_this_activation"
    assert (
        summary["decisions"][1]["outcome"] == "forbid response actions tied to this activation id"
    )


def test_architecture_validation_borrowing_notes():
    summary = run_borrowing_notes()
    assert "typed seam-as-contract" in summary["affairon"]["borrow"]
    assert "event-class ergonomics" in summary["moduvent"]["borrow"]


def test_architecture_validation_cannot_draw():
    summary = run_cannot_draw()
    assert summary["scenario"] == "cannot_draw"
    assert (
        summary["interactions"][2]["outcome"]
        == "resolve to forbidden because forbid outranks grant"
    )


def test_architecture_validation_cannot_activate_monster_effects():
    summary = run_cannot_activate_monster_effects()
    assert summary["scenario"] == "cannot_activate_monster_effects"
    assert (
        summary["interactions"][3]["outcome"]
        == "hide monster-effect activation actions while preserving other legal actions"
    )


def test_architecture_validation_destruction_replacement():
    summary = run_destruction_replaced_with_banish()
    assert summary["scenario"] == "destruction_replaced_with_banish"
    assert (
        summary["interactions"][2]["outcome"]
        == "rewrite pending effect outcome from destroy to banish before commit"
    )


def test_architecture_validation_continuous_atk_modifier():
    summary = run_continuous_atk_modifier()
    assert summary["scenario"] == "continuous_atk_modifier"
    assert (
        summary["interactions"][3]["outcome"]
        == "expose derived ATK in views without mutating base stat storage"
    )
