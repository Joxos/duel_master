from __future__ import annotations

from typing import TYPE_CHECKING

from duel_core.mr2020.duel.affairs import DuelAffairWithRequester
from duel_core.mr2020.timing.affairs import ExposedUserAction

if TYPE_CHECKING:
    from duel_core.mr2020.player.models import Player


class Draw(DuelAffairWithRequester, ExposedUserAction):
    player: Player
    num: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Draw):
            return False
        return super().__eq__(other) and self.player is other.player and self.num == other.num


def rebuild_draw_models(namespace: dict[str, object]) -> None:
    Draw.model_rebuild(_types_namespace=namespace)
