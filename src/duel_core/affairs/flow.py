from __future__ import annotations

from collections.abc import Callable

from pydantic import Field

from duel_core.affairs.base import ActionableDuelAffair, DuelAffair, ExecutableAffair
from duel_core.phase import Phase
from duel_core.affairs.turn import EnterPhase


class DuelInit(DuelAffair):
    pass


class AvailableActions(DuelAffair):
    actions: list[ExecutableAffair] = Field(default_factory=list)


class CompletedAffair(DuelAffair):
    affair: DuelAffair


def completed_affair_of(*affair_types: type[DuelAffair]) -> Callable[[CompletedAffair], bool]:
    def _matches(completed: CompletedAffair) -> bool:
        return isinstance(completed.affair, affair_types)

    return _matches


def completed_enter_phase(phase: Phase) -> Callable[[CompletedAffair], bool]:
    def _matches(completed: CompletedAffair) -> bool:
        return isinstance(completed.affair, EnterPhase) and completed.affair.phase is phase

    return _matches


def completed_multi_origin_of(*affair_types: type[DuelAffair]) -> Callable[[CompletedAffair], bool]:
    def _matches(completed: CompletedAffair) -> bool:
        return isinstance(completed.affair, MultiAffair) and isinstance(
            completed.affair.origin, affair_types
        )

    return _matches


class MultiAffair(ActionableDuelAffair):
    origin: DuelAffair
    children: list[DuelAffair] = Field(default_factory=list)
