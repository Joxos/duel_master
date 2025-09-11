from .enumerations import PHASE
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Duel


class Action:
    def __init__(self):
        pass

    def available(self, duel: "Duel") -> bool:
        return False

    def perform(self, duel: "Duel"):
        pass


class NextPhase(Action):
    def __init__(self, _from: PHASE, to: PHASE):
        self._from = _from
        self.to = to
