from __future__ import annotations

from .enums import TurnPhase, TurnStep


PHASE_SEQUENCE: tuple[TurnPhase, ...] = (
    TurnPhase.DRAW,
    TurnPhase.STANDBY,
    TurnPhase.MAIN1,
    TurnPhase.BATTLE,
    TurnPhase.MAIN2,
    TurnPhase.END,
)

STEP_SEQUENCE_BATTLE: tuple[TurnStep, ...] = (
    TurnStep.BATTLE_START,
    TurnStep.DAMAGE_STEP,
    TurnStep.DAMAGE_END,
)


def first_turn_no_draw(
    turn_number: int, current_player_index: int, first_player_index: int
) -> bool:
    return turn_number == 1 and current_player_index == first_player_index


def next_player_index(current_player_index: int, player_count: int = 2) -> int:
    return (current_player_index + 1) % player_count
