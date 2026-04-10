from __future__ import annotations

from typing import TYPE_CHECKING

from duel_core.affairs.base import ActionableDuelAffair, AtomicAction, DuelAffair, ExecutableAffair
from duel_core.models import REPRESENTATION

if TYPE_CHECKING:
    from duel_core.models import Player, RuntimeCard


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


class DrawCard(AtomicAction):
    player: Player
    card: RuntimeCard


class NormalSummon(ExecutableAffair):
    player: Player
    card: RuntimeCard
    from_hand_index: int
    to_monster_zone_index: int
    from_representation: REPRESENTATION
    to_representation: REPRESENTATION
    normal_summon_used_from: bool
    normal_summon_used_to: bool

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


class SendToGraveyard(AtomicAction):
    player: Player
    card: RuntimeCard
    from_monster_zone_index: int
    to_graveyard_index: int
    from_representation: REPRESENTATION
    to_representation: REPRESENTATION


class LpVary(AtomicAction):
    player: Player
    delta: int


class Forbid(DuelAffair):
    target: ActionableDuelAffair
    inactive_from_turn: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Forbid):
            return False
        return self.target == other.target
