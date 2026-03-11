from __future__ import annotations

from dataclasses import dataclass

from .enums import TurnPhase, TurnStep
from .rules import (
    PHASE_SEQUENCE,
    STEP_SEQUENCE_BATTLE,
    first_turn_no_draw,
    next_player_index,
)


@dataclass(frozen=True, slots=True)
class PhaseMachine:
    current_phase: TurnPhase = TurnPhase.DRAW
    current_step: TurnStep | None = None
    turn_number: int = 1
    current_player_index: int = 0
    first_player_index: int = 0

    def can_transition(
        self,
        to_phase: TurnPhase,
        to_step: TurnStep | None = None,
    ) -> bool:
        if self.current_phase == TurnPhase.BATTLE and to_phase == TurnPhase.BATTLE:
            return self._can_transition_battle_step(to_step)

        if to_step is not None:
            return False

        if self.current_phase == TurnPhase.DRAW and first_turn_no_draw(
            self.turn_number,
            self.current_player_index,
            self.first_player_index,
        ):
            return to_phase == TurnPhase.STANDBY

        current_index = PHASE_SEQUENCE.index(self.current_phase)
        if current_index < len(PHASE_SEQUENCE) - 1:
            return to_phase == PHASE_SEQUENCE[current_index + 1]
        return to_phase == TurnPhase.DRAW

    def advance(
        self,
        to_phase: TurnPhase | None = None,
        to_step: TurnStep | None = None,
    ) -> "PhaseMachine":
        if self.current_phase == TurnPhase.BATTLE and to_phase == TurnPhase.BATTLE:
            if not self.can_transition(to_phase, to_step):
                raise ValueError(
                    f"Invalid transition from {self.current_phase}/{self.current_step} "
                    f"to {to_phase}/{to_step}"
                )
            return PhaseMachine(
                current_phase=TurnPhase.BATTLE,
                current_step=to_step,
                turn_number=self.turn_number,
                current_player_index=self.current_player_index,
                first_player_index=self.first_player_index,
            )

        if to_phase is None:
            if self.current_phase == TurnPhase.BATTLE and self.current_step is None:
                to_phase = TurnPhase.BATTLE
                to_step = TurnStep.BATTLE_START
            else:
                to_phase = self._next_phase()

        if not self.can_transition(to_phase, to_step):
            raise ValueError(
                f"Invalid transition from {self.current_phase}/{self.current_step} "
                f"to {to_phase}/{to_step}"
            )

        if self.current_phase == TurnPhase.END and to_phase == TurnPhase.DRAW:
            return PhaseMachine(
                current_phase=TurnPhase.DRAW,
                current_step=None,
                turn_number=self.turn_number + 1,
                current_player_index=next_player_index(self.current_player_index),
                first_player_index=self.first_player_index,
            )

        return PhaseMachine(
            current_phase=to_phase,
            current_step=TurnStep.BATTLE_START
            if to_phase == TurnPhase.BATTLE and to_step is None
            else to_step,
            turn_number=self.turn_number,
            current_player_index=self.current_player_index,
            first_player_index=self.first_player_index,
        )

    def _next_phase(self) -> TurnPhase:
        if self.current_phase == TurnPhase.DRAW and first_turn_no_draw(
            self.turn_number,
            self.current_player_index,
            self.first_player_index,
        ):
            return TurnPhase.STANDBY

        current_index = PHASE_SEQUENCE.index(self.current_phase)
        if current_index == len(PHASE_SEQUENCE) - 1:
            return TurnPhase.DRAW
        return PHASE_SEQUENCE[current_index + 1]

    def _can_transition_battle_step(self, to_step: TurnStep | None) -> bool:
        if to_step is None:
            return False

        if self.current_step is None:
            return to_step == TurnStep.BATTLE_START

        current_index = STEP_SEQUENCE_BATTLE.index(self.current_step)
        if current_index < len(STEP_SEQUENCE_BATTLE) - 1:
            return to_step == STEP_SEQUENCE_BATTLE[current_index + 1]
        return False
