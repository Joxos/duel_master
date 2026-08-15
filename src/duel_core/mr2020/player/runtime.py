from __future__ import annotations

from duel_core.mr2020.player.models import Player


class PlayerRuntime:
    def __init__(self, players: tuple[Player, Player], *, current_player: Player) -> None:
        self.players = players
        self.current_player = current_player

    def set_current_player(self, player: Player) -> None:
        self.current_player = player

    def opponent_of(self, player: Player) -> Player:
        if player is self.players[0]:
            return self.players[1]
        if player is self.players[1]:
            return self.players[0]
        raise ValueError("Player must be one of the duel players")
