from __future__ import annotations

from duel_core.models import MutableModel
from duel_core.phase import Phase
from duel_core.mr2020.models.player import Player


class DuelState(MutableModel):
    players: tuple[Player, Player]
    current_player: Player
    current_turn_count: int
    phase: Phase
    normal_summon_used: bool = False

    def opponent_of(self, player: Player) -> Player:
        if player is self.players[0]:
            return self.players[1]
        if player is self.players[1]:
            return self.players[0]
        raise ValueError("Player must be one of the duel players")

    def observe(self, view: Player):
        if view not in self.players:
            raise ValueError("Player must be one of the duel players")
        from duel_core.mr2020.models.view import PlayerView

        return PlayerView.from_state(self, viewer=view)
