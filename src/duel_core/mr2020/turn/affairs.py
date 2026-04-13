from __future__ import annotations

from typing import TYPE_CHECKING

from duel_core.mr2020.duel.affairs import DuelAffair
from duel_core.mr2020.timing.affairs import AtomicAction

if TYPE_CHECKING:
    from duel_core.mr2020.player.models import Player


class AdvanceTurn(DuelAffair, AtomicAction):
    from_turn: int
    to_turn: int
    from_player: Player
    to_player: Player


def rebuild_turn_models(namespace: dict[str, object]) -> None:
    AdvanceTurn.model_rebuild(_types_namespace=namespace)
