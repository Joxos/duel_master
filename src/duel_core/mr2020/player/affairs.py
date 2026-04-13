from __future__ import annotations

from typing import TYPE_CHECKING

from duel_core.mr2020.duel.affairs import DuelAffair

if TYPE_CHECKING:
    from duel_core.mr2020.player.models import Player


class SetPlayers(DuelAffair):
    players: tuple[Player, Player]
    starting_player: Player


def rebuild_player_affairs(namespace: dict[str, object]) -> None:
    SetPlayers.model_rebuild(_types_namespace=namespace)
