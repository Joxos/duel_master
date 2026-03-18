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

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented

        if not isinstance(other, ActionableDuelAffair):
            return NotImplemented

        return self.requester is other.requester


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
        if self.phase is Phase.MAIN_1:
            return "Enter Main Phase 1"
        if self.phase is Phase.MAIN_2:
            return "Enter Main Phase 2"
        return f"Enter {self.phase.value} Phase"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EnterPhase):
            return NotImplemented

        return (
            self.requester is other.requester
            and self.source_phase is other.source_phase
            and self.phase is other.phase
        )


class ExitPhase(ExecutableAffair):
    phase: Phase


class TurnCleanup(DuelAffair):
    turn: int


class Draw(ExecutableAffair):
    player: Player
    num: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Draw):
            return NotImplemented

        return (
            self.requester is other.requester
            and self.player is other.player
            and self.num == other.num
        )


class Forbid(DuelAffair):
    target: ActionableDuelAffair
    outdated_when: TurnCleanup

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Forbid):
            return NotImplemented

        return self.target == other.target
