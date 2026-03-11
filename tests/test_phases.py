import pytest

from duel_engine.phases import PhaseMachine, TurnPhase, TurnStep, first_turn_no_draw


def test_turn_flow_baseline_first_turn_skips_draw_for_starting_player():
    machine = PhaseMachine(
        current_phase=TurnPhase.DRAW,
        turn_number=1,
        current_player_index=0,
        first_player_index=0,
    )

    assert first_turn_no_draw(
        turn_number=machine.turn_number,
        current_player_index=machine.current_player_index,
        first_player_index=machine.first_player_index,
    )

    machine = machine.advance()
    assert machine.current_phase == TurnPhase.STANDBY
    assert machine.current_step is None


def test_turn_flow_baseline_non_first_turn_runs_full_phase_order():
    machine = PhaseMachine(
        current_phase=TurnPhase.DRAW,
        turn_number=2,
        current_player_index=1,
        first_player_index=0,
    )

    machine = machine.advance()
    assert machine.current_phase == TurnPhase.STANDBY

    machine = machine.advance()
    assert machine.current_phase == TurnPhase.MAIN1

    machine = machine.advance()
    assert machine.current_phase == TurnPhase.BATTLE
    assert machine.current_step == TurnStep.BATTLE_START

    machine = machine.advance(to_phase=TurnPhase.BATTLE, to_step=TurnStep.DAMAGE_STEP)
    assert machine.current_step == TurnStep.DAMAGE_STEP

    machine = machine.advance(to_phase=TurnPhase.BATTLE, to_step=TurnStep.DAMAGE_END)
    assert machine.current_step == TurnStep.DAMAGE_END

    machine = machine.advance(to_phase=TurnPhase.MAIN2)
    assert machine.current_phase == TurnPhase.MAIN2
    assert machine.current_step is None

    machine = machine.advance()
    assert machine.current_phase == TurnPhase.END


def test_turn_flow_baseline_end_phase_passes_turn_to_next_player():
    machine = PhaseMachine(
        current_phase=TurnPhase.END,
        turn_number=3,
        current_player_index=0,
        first_player_index=0,
    )

    next_turn = machine.advance()

    assert next_turn.current_phase == TurnPhase.DRAW
    assert next_turn.current_step is None
    assert next_turn.turn_number == 4
    assert next_turn.current_player_index == 1


def test_turn_flow_baseline_rejects_invalid_transition():
    machine = PhaseMachine(current_phase=TurnPhase.MAIN1)

    with pytest.raises(ValueError):
        machine.advance(to_phase=TurnPhase.END)
