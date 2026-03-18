from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from affairon import MutableAffair
from pydantic import ConfigDict, Field

from duel_core.phase import Phase

if TYPE_CHECKING:
    from duel_core.duel import Duel
    from duel_core.models import Player


class DuelAffair(MutableAffair):
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        strict=True,
        arbitrary_types_allowed=True,
    )

    duel: Duel


class ActionableDuelAffair(DuelAffair):
    requester: Callable[..., object]


class ExecutableAffair(ActionableDuelAffair):
    label: str | None = None


class DuelInit(DuelAffair):
    pass


class AvailableActions(DuelAffair):
    actions: list[ExecutableAffair] = Field(default_factory=list)


class ExecutionRequest(DuelAffair):
    affair: ExecutableAffair


class CompletedAffair(DuelAffair):
    affair: ExecutableAffair


class MultiAffair(ExecutableAffair):
    children: list[DuelAffair] = Field(default_factory=list)


class EnterPhase(ExecutableAffair):
    phase: Phase
    source_phase: Phase

    def __str__(self) -> str:
        labels = {
            Phase.DRAW: "Enter Draw Phase",
            Phase.STANDBY: "Enter Standby Phase",
            Phase.MAIN_1: "Enter Main Phase 1",
            Phase.BATTLE: "Enter Battle Phase",
            Phase.MAIN_2: "Enter Main Phase 2",
            Phase.END: "Enter End Phase",
        }
        return labels[self.phase]


class ExitPhase(ExecutableAffair):
    phase: Phase


class TurnCleanup(DuelAffair):
    turn: int


class Draw(ExecutableAffair):
    player: Player
    num: int


class Forbid(DuelAffair):
    target: Callable[..., object]
    outdated_when: TurnCleanup
    source_phase: Phase | None = None
    target_phase: Phase | None = None
