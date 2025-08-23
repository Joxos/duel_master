from moduvent import Event
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Duel, Player


class DuelInitialize(Event):
    def __init__(self, player_1: "Player", player_2: "Player"):
        super().__init__()
        self.player_1 = player_1
        self.player_2 = player_2


class DuelStateEvent(Event):
    def __init__(self, duel: "Duel"):
        super().__init__()
        self.duel = duel


class DuelStart(DuelStateEvent):
    def __init__(self, duel: "Duel"):
        super().__init__(duel)


class ShowAndGetAction(DuelStateEvent):
    def __init__(self, duel: "Duel"):
        super().__init__(duel)


class PerformAction(DuelStateEvent):
    def __init__(self, duel: "Duel", action):
        super().__init__(duel)
        self.action = action


class NextTurn(DuelStateEvent):
    def __init__(self, duel: "Duel", player: "Player"):
        super().__init__(duel)
        self.player = player
