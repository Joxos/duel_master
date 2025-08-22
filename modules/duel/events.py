from moduvent import Event
from .models import Player


class DuelInitialize(Event):
    def __init__(self, player_1: Player, player_2: Player):
        super().__init__()
        self.player_1 = player_1
        self.player_2 = player_2


class DuelStart(Event):
    def __init__(self):
        super().__init__()


class ShowAndGetAction(Event):
    def __init__(self):
        super().__init__()


class PerformAction(Event):
    def __init__(self, action):
        super().__init__()
        self.action = action


class TurnChance(Event):
    def __init__(self, player: Player):
        super().__init__()
        self.player = player
