"""Typed affair definitions for the current duel slice.

This module defines the event and executable-affair surface used to connect the
public facade, rules, and kernel execution seams.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from affairon import MutableAffair
from pydantic import ConfigDict, Field

from duel_core.phase import Phase

if TYPE_CHECKING:
    from duel_core.duel import Duel
    from duel_core.models import Card, Player


class DuelAffair(MutableAffair):
    """Base affair carrying duel context through the runtime graph.

    Attributes:
        duel: Duel instance that owns the current execution graph.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        strict=True,
        arbitrary_types_allowed=True,
    )

    duel: Duel


class ActionableDuelAffair(DuelAffair):
    """Affair whose semantic source matters for identity checks.

    Attributes:
        requester: Callable that contributed or requested this affair.
    """

    requester: Callable[..., object]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ActionableDuelAffair):
            return False

        return self.requester is other.requester


class ExecutableAffair(ActionableDuelAffair):
    """Affair that can be surfaced to the user as an executable action.

    Attributes:
        label: Optional presentation label for UI surfaces.
    """

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
            return False

        requester_match = super().__eq__(other)
        source_match = self.source_phase is other.source_phase
        phase_match = self.phase is other.phase
        return requester_match and source_match and phase_match


class ExitPhase(ExecutableAffair):
    phase: Phase


class TurnCleanup(DuelAffair):
    turn: int


class Draw(ExecutableAffair):
    player: Player
    num: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Draw):
            return False

        requester_match = super().__eq__(other)
        player_match = self.player is other.player
        draw_num_match = self.num == other.num
        return requester_match and player_match and draw_num_match


class NormalSummon(ExecutableAffair):
    player: Player
    card: Card

    def __str__(self) -> str:
        return f"Normal Summon {self.card.name}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NormalSummon):
            return False

        requester_match = super().__eq__(other)
        player_match = self.player is other.player
        card_match = self.card == other.card
        return requester_match and player_match and card_match


class Forbid(DuelAffair):
    target: ActionableDuelAffair
    outdated_when: TurnCleanup

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Forbid):
            return False

        return self.target == other.target
