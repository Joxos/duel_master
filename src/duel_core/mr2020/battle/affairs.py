from __future__ import annotations

from typing import TYPE_CHECKING

from duel_core.mr2020.duel.affairs import DuelAffairWithRequester
from duel_core.mr2020.timing.affairs import ExposedUserAction

if TYPE_CHECKING:
    from duel_core.mr2020.card.models import RuntimeCard
    from duel_core.mr2020.player.models import Player


class Attack(DuelAffairWithRequester, ExposedUserAction):
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


def rebuild_battle_models(namespace: dict[str, object]) -> None:
    for model in (Attack,):
        model.model_rebuild(_types_namespace=namespace)
