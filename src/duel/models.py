from typing import TYPE_CHECKING, List, Optional

from actions.models import Action
from phase.enum import PHASE
from phase.events import TurnChance
from phase.models import PhaseWithPlayer

if TYPE_CHECKING:
    from cards.models import Card
    from player.models import Player


class History(list[Action]):
    def current_turn(self) -> List[Action]:
        return next(
            (
                self[i + 1 :]
                for i in range(len(self) - 1, -1, -1)
                if isinstance(self[i], TurnChance)
            ),
            [],
        )


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

        self.phase = PhaseWithPlayer(PHASE.DRAW, player_1)
        self.turn_count = 1
        self.history = History()
        self.all_cards = []

    @property
    def current_player(self) -> "Player":
        return self.phase.player

    @property
    def current_phase(self) -> "PHASE":
        return self.phase.phase

    @property
    def opponent_player(self) -> "Player":
        return self.other_player(self.current_player)

    def other_player(self, player: "Player") -> "Player":
        return self.player_1 if player == self.player_2 else self.player_2
