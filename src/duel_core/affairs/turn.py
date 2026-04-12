from __future__ import annotations

from typing import TYPE_CHECKING

from duel_core.affairs.base import AtomicAction, ExposedUserAction
from duel_core.phase import Phase

if TYPE_CHECKING:
    from duel_core.mr2020.models import Player


class EnterPhase(ExposedUserAction):
    phase: Phase
    source_phase: Phase

    def __str__(self) -> str:
        if self.phase is Phase.MAIN_1:
            return "Enter Main Phase 1"
        if self.phase is Phase.MAIN_2:
            return "Enter Main Phase 2"
        return f"Enter {self.phase.value} Phase"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EnterPhase):
            return False

        requester_match = super().__eq__(other)
        source_match = self.source_phase is other.source_phase
        phase_match = self.phase is other.phase
        return requester_match and source_match and phase_match


class ExitPhase(ExposedUserAction):
    phase: Phase


class AdvanceTurn(AtomicAction):
    from_turn: int
    to_turn: int
    from_player: Player
    to_player: Player
    normal_summon_used_from: bool
    normal_summon_used_to: bool
