from __future__ import annotations

from typing import TYPE_CHECKING

from duel_core.mr2020.player.models import Player
from duel_core.mr2020.player.runtime import PlayerRuntime
from duel_core.mr2020.view.models import PlayerView

if TYPE_CHECKING:
    from duel_core.mr2020.duel.models import Duel


class ViewRuntime:
    def __init__(self, duel: Duel) -> None:
        self.duel = duel

    def observe(self, player: Player) -> PlayerView:
        if player not in self.duel.inject(PlayerRuntime).players:
            raise ValueError("Player must be one of the duel players")
        return PlayerView.from_duel(duel=self.duel, viewer=player)
