from __future__ import annotations

from typing import TYPE_CHECKING

from duel_core.mr2020.duel.affairs import DuelAffair
from duel_core.mr2020.timing.affairs import AtomicAction

if TYPE_CHECKING:
    from duel_core.mr2020.player.models import Player


class LpVary(DuelAffair, AtomicAction):
    player: Player
    delta: int


def rebuild_life_point_models(namespace: dict[str, object]) -> None:
    LpVary.model_rebuild(_types_namespace=namespace)
