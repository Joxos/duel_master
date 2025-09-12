from .enumerations import PHASE, CARD
from typing import TYPE_CHECKING
from .log import logger

if TYPE_CHECKING:
    from .models import Duel, PhaseWithPlayer, Card


class Action:
    def __init__(self):
        pass

    def available(self, duel: "Duel") -> bool:
        return False

    def perform(self, duel: "Duel"):
        duel.history.append(self)


class NextPhase(Action):
    def __init__(self, _from: "PhaseWithPlayer", to: "PhaseWithPlayer"):
        self._from = _from
        self.to = to

    def available(self, duel: "Duel") -> bool:
        initial_phase_correct = duel.phase == self._from
        consequence = (
            PHASE.CONSEQUENCE if duel.turn_count > 1 else PHASE.CONSEQUENCE_OF_TURN_1
        )
        phase_consequence_correct = (
            self._from.phase in consequence
            and self.to.phase in consequence[self._from.phase]
        )
        player_correct = (
            self._from.player != self.to.player
            if self._from.phase == PHASE.END and self.to.phase == PHASE.DRAW
            else self._from.player == self.to.player
        )
        if initial_phase_correct and phase_consequence_correct and player_correct:
            return True
        else:
            logger.debug(
                f"NextPhase not available: {self._from} -> {self.to} with initial_phase_correct: {initial_phase_correct}, phase_consequence_correct: {phase_consequence_correct}, player_correct: {player_correct}"
            )
            return False

    def perform(self, duel):
        super().perform(duel)
        duel.next_phase(self.to)

    def __str__(self):
        return f"Change phase from {self._from} to {self.to}"


class NormalSummon(Action):
    def __init__(self, card: "Card"):
        self.card = card

    def available(self, duel: "Duel"):
        phase_correct = duel.phase.phase in [PHASE.MAIN1, PHASE.MAIN2]
        card_correct = self.card.type == CARD.MONSTER
        level_correct = self.card.level <= 4
        if phase_correct and card_correct and level_correct:
            return True
        else:
            logger.debug(
                f"NormalSummon not available: {self.card} with phase_correct: {phase_correct}, card_correct: {card_correct}, level_correct: {level_correct}"
            )
            return False

    def perform(self, duel: "Duel"):
        super().perform(duel)
        duel.player.hand.remove(self.card)
        duel.player.field.append(self.card)


def show_action(actions: list[Action]):
    print("Available actions:")
    for index, action in enumerate(actions):
        logger.info(f"{index}: {action}")
