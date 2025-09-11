from .enumerations import PHASE
from typing import TYPE_CHECKING
from .log import logger

if TYPE_CHECKING:
    from .models import Duel, PhaseWithPlayer


class Action:
    def __init__(self):
        pass

    def available(self, duel: "Duel") -> bool:
        return False

    def perform(self, duel: "Duel"):
        pass


class NextPhase(Action):
    def __init__(self, _from: "PhaseWithPlayer", to: "PhaseWithPlayer"):
        self._from = _from
        self.to = to

    def available(self, duel: "Duel") -> bool:
        if duel.phase == self._from:
            consequence = (
                PHASE.CONSEQUENCE
                if duel.turn_count > 1
                else PHASE.CONSEQUENCE_OF_TURN_1
            )
            if self.to.phase in consequence[self._from.phase]:
                if self._from.phase == PHASE.END and self.to.phase == PHASE.DRAW:
                    logger.debug(
                        f"NextPhase action available if {self.to.player} is waiting player ({self.to.player} == {duel.waiting_player()})"
                    )
                    return self.to.player == duel.waiting_player()
                else:
                    logger.debug(
                        f"NextPhase action available: valid phase transition from {self._from.phase} to {self.to.phase}"
                    )
                    return True
            else:
                logger.debug(
                    f"NextPhase action not available: invalid phase transition from {self._from.phase} to {self.to.phase}"
                )
        else:
            logger.debug(
                f"NextPhase action not available: current phase {duel.phase}, required {self._from}"
            )
        return False

    def perform(self, duel):
        duel.next_phase(self.to)


def show_action(actions: list[Action]):
    print("Available actions:")
    for index, action in enumerate(actions):
        if isinstance(action, NextPhase):
            print(f"{index}: Change phase from {action._from} to {action.to}")
