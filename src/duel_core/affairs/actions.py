from __future__ import annotations

from typing import TYPE_CHECKING

from duel_core.affairs.base import DuelAffairWithRequester, AtomicAction, DuelAffair, ExposedUserAction
from duel_core.models import REPRESENTATION

if TYPE_CHECKING:
    from duel_core.models import Player, RuntimeCard, Zone


class Draw(ExposedUserAction):
    player: Player
    num: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Draw):
            return False

        requester_match = super().__eq__(other)
        player_match = self.player is other.player
        draw_num_match = self.num == other.num
        return requester_match and player_match and draw_num_match


class MoveCard(AtomicAction):
    player: Player
    card: RuntimeCard
    from_area: str
    to_area: str
    from_zone: Zone | None = None
    to_zone: Zone | None = None
    from_representation: REPRESENTATION
    to_representation: REPRESENTATION


class Attack(ExposedUserAction):
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


class LpVary(AtomicAction):
    player: Player
    delta: int


class Forbid(DuelAffair):
    target: DuelAffairWithRequester
    inactive_from_turn: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Forbid):
            return False
        return self.target == other.target
