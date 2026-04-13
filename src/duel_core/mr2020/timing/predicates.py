from __future__ import annotations

from collections.abc import Callable

from duel_core.mr2020.duel.affairs import CompletedAffair, DuelAffair, MultiAction
from duel_core.mr2020.phase.affairs import EnterPhase
from duel_core.mr2020.phase.models import Phase


def completed_affair_of(*affair_types: type[DuelAffair]) -> Callable[[CompletedAffair], bool]:
    def _matches(completed: CompletedAffair) -> bool:
        return isinstance(completed.affair, affair_types)

    return _matches


def completed_enter_phase(phase: Phase) -> Callable[[CompletedAffair], bool]:
    def _matches(completed: CompletedAffair) -> bool:
        return isinstance(completed.affair, EnterPhase) and completed.affair.phase is phase

    return _matches


def completed_multi_action_origin_of(
    *affair_types: type[DuelAffair],
) -> Callable[[CompletedAffair], bool]:
    def _matches(completed: CompletedAffair) -> bool:
        return isinstance(completed.affair, MultiAction) and isinstance(
            completed.affair.origin, affair_types
        )

    return _matches
