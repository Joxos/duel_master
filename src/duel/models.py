from typing import TYPE_CHECKING, Optional

from phase.enum import PHASE
from phase.models import PhaseWithPlayer

if TYPE_CHECKING:
    from cards.models import Card
    from player.models import Player

class Duel:
    def __init__(self, player_1: "Player", player_2: "Player"):
        self.player_1 = player_1
        self.player_2 = player_2

        self.extra_monster_zone_1: Optional[Card] = None
        self.extra_monster_zone_2: Optional[Card] = None
        self.extra_monster_zones = [
            self.extra_monster_zone_1,
            self.extra_monster_zone_2,
        ]

        self.phase = PhaseWithPlayer(PHASE.STANDBY, player_1)
        self.turn_count = 0
        self.history = []

    def current_player(self) -> "Player":
        return self.player_2 if self.turn_count % 2 == 0 else self.player_1

    def another_player(self) -> "Player":
        return self.player_1 if self.turn_count % 2 == 0 else self.player_2

    def opponent_player(self, player: "Player") -> "Player":
        return self.player_1 if player == self.player_2 else self.player_2
