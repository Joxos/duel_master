from __future__ import annotations

from collections.abc import Callable

from pydantic import Field

from duel_core.affairs.base import DuelAffairWithRequester, DuelAffair, ExposedUserAction
from duel_core.phase import Phase
from duel_core.affairs.turn import EnterPhase


class DuelInit(DuelAffair):
    """This affair signals the start of a duel execution, carrying the initial state and context. It is emitted once at the beginning of the duel flow and can be listened to for setup purposes.
    """
    pass


class AvailableActions(DuelAffair):
    """This affair represents the set of actions currently available to the player. It is the entry point for user interaction in the duel flow. Listeners can populate the `actions` attribute with actionable affairs that the player can execute in the current context.
    """
    actions: list[ExposedUserAction] = Field(default_factory=list)


class CompletedAffair(DuelAffair):
    """This affair is emitted from the kernel to the duel-level dispatcher whenever an affair has completed execution. It carries the completed affair and can be listened to for triggering subsequent effects or flow transitions based on the completion of specific affairs.
    """
    affair: DuelAffair


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


class MultiAction(DuelAffairWithRequester):
    """This affair represents a composite action that consists of multiple child affairs. It is used to group together a sequence of affairs that should be executed as a unit, often originating from a single user action or effect. The `requester` attribute indicates the source of the multi-action, while the `origin` attribute can carry the initial affair that triggered the multi-action, allowing for traceability and context during execution.
    """
    origin: DuelAffair
    children: list[DuelAffair] = Field(default_factory=list)
