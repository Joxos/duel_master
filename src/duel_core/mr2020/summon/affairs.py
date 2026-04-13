from __future__ import annotations

from typing import TYPE_CHECKING

from duel_core.mr2020.duel.affairs import DuelAffairWithRequester
from duel_core.mr2020.timing.affairs import ExposedUserAction

if TYPE_CHECKING:
    from duel_core.mr2020.card.models import REPRESENTATION, RuntimeCard
    from duel_core.mr2020.player.models import Player, Zone


class NormalSummon(DuelAffairWithRequester, ExposedUserAction):
    player: Player
    card: RuntimeCard
    to_zone: Zone
    from_representation: REPRESENTATION
    to_representation: REPRESENTATION

    def __str__(self) -> str:
        return f"Normal Summon {self.card.card.name}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NormalSummon):
            return False
        return (
            super().__eq__(other)
            and self.player is other.player
            and self.card == other.card
            and self.to_zone is other.to_zone
        )


def rebuild_summon_models(namespace: dict[str, object]) -> None:
    NormalSummon.model_rebuild(_types_namespace=namespace)
