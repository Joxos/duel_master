from moduvent import Event
from .enumerations import END_REASON
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Duel, Player, Card


class DuelInitialize(Event):
    def __init__(self, player_1: "Player", player_2: "Player"):
        super().__init__()
        self.player_1 = player_1
        self.player_2 = player_2


class DuelStateEvent(Event):
    """
    Every DuelStateEvent requires a Duel instance.
    This can be helpful when server has multiple duels to manage.
    """

    def __init__(self, duel: "Duel"):
        super().__init__()
        self.duel = duel


class DuelStart(DuelStateEvent):
    def __init__(self, duel: "Duel"):
        super().__init__(duel)


class DuelPreparation(DuelStateEvent):
    """Do preparations here."""

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


class EnterPhase(DuelStateEvent):
    def __init__(self, duel: "Duel", phase):
        super().__init__(duel)
        self.phase = phase


class ExitPhase(DuelStateEvent):
    def __init__(self, duel: "Duel", phase):
        super().__init__(duel)
        self.phase = phase


class OnNormalSummon(DuelStateEvent):
    def __init__(self, duel: "Duel", player: "Player", card: "Card"):
        super().__init__(duel)
        self.player = player
        self.card = card


class OnSpecialSummon(DuelStateEvent):
    def __init__(self, duel: "Duel", player: "Player", card: "Card"):
        super().__init__(duel)
        self.player = player
        self.card = card


class DuelEnd(DuelStateEvent):
    def __init__(self, duel: "Duel", reason: END_REASON, win_player: "Player"):
        super().__init__(duel)
        self.reason = reason
        self.win_player = win_player
