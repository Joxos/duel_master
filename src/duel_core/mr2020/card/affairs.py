from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from duel_core.mr2020.duel.affairs import DuelAffair
from duel_core.mr2020.timing.affairs import AtomicAction

if TYPE_CHECKING:
    from duel_core.mr2020.card.models import REPRESENTATION, RuntimeCard
    from duel_core.mr2020.player.models import Player, Zone

Area = Literal["graveyard", "hand", "main_deck", "monster_zone"]


class MoveCard(DuelAffair, AtomicAction):
    player: Player
    card: RuntimeCard
    from_area: Area
    to_area: Area
    from_zone: Zone | None = None
    to_zone: Zone | None = None
    from_representation: REPRESENTATION
    to_representation: REPRESENTATION


def rebuild_card_affairs(namespace: dict[str, object]) -> None:
    MoveCard.model_rebuild(_types_namespace=namespace)
