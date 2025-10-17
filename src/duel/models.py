from typing import TYPE_CHECKING, List, Optional

from actions.events import Action
from effects.models import Chain
from phase.enum import PHASE
from phase.events import TurnChance
from phase.models import PhaseWithPlayer

if TYPE_CHECKING:
    from cards.models import Card
    from player.models import Player


class History(list):
    def slice_back_until(self, action_type):
        return next(
            (
                self[i:]
                for i in range(len(self) - 1, -1, -1)
                if isinstance(self[i], action_type)
                or issubclass(action_type, type(self[i]))
            ),
            [],
        )

    def current_turn_actions(self) -> List:
        return self.slice_back_until(TurnChance)

    def current_occasions(self) -> List:
        return self.slice_back_until(Action)


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
        self.current_chain = Chain()
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
