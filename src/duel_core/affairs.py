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
    from duel_core.models import Player, RuntimeCard


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
    action: ExecutableAffair
    result: DuelAffair


class MultiAffair(ActionableDuelAffair):
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
    card: RuntimeCard

    def __str__(self) -> str:
        return f"Normal Summon {self.card.card.name}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NormalSummon):
            return False
        return super().__eq__(other) and self.player is other.player and self.card == other.card


class Attack(ExecutableAffair):
    player: Player
    attacker: RuntimeCard
    defender: RuntimeCard | None = None

    def __str__(self) -> str:
        if self.defender is None:
            return f"Direct Attack with {self.attacker.card.name}"
        return f"Attack with {self.attacker.card.name}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Attack):
            return False
        return (
            super().__eq__(other)
            and self.player is other.player
            and self.attacker == other.attacker
            and self.defender == other.defender
        )


class SendToGraveyard(DuelAffair):
    player: Player
    card: RuntimeCard


class LpVary(DuelAffair):
    player: Player
    delta: int


class Forbid(DuelAffair):
    target: ActionableDuelAffair
    outdated_when: TurnCleanup

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Forbid):
            return False
        return self.target == other.target


class Concede(DuelAffair):
    """A player's voluntary surrender of the duel.

    Attributes:
        player: The player who surrenders.
    """

    player: Player


class MatchEnd(DuelAffair):
    """Signals the end of a duel with a declared winner.

    Emitted by the victory-condition rule plugin once a win condition is
    satisfied, and consumed by the kernel to finalize duel state.

    Attributes:
        winner: The player who won the duel.
        loser: The player who lost the duel.
        reason: Machine-readable victory condition identifier.
    """

    winner: Player
    loser: Player
    reason: str
