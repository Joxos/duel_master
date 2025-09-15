from .enumerations import PHASE, CARD, CardStatus, LOCATION, EXPRESSION_WAY, FACE
from typing import TYPE_CHECKING
from .log import logger

if TYPE_CHECKING:
    from .models import Duel, PhaseWithPlayer, Card, Player, Effect


class Flag:
    def __init__(self):
        pass


class Condition:
    def __init__(self):
        pass

    def available(self, duel: "Duel") -> bool:
        return False


class Action(Condition):
    def perform(self, duel: "Duel"):
        duel.history.append(self)


class NextPhase(Action):
    def __init__(self, duel: "Duel", _from: "PhaseWithPlayer", to: "PhaseWithPlayer"):
        self.duel = duel
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

    def __eq__(self, value):
        if not isinstance(value, NextPhase):
            return False
        return self._from == value._from and self.to == value.to

    def __str__(self):
        return f"Change phase from {self._from} to {self.to}"


class NormalSummon(Action):
    def __init__(self, card: "Card"):
        self.card = card

    def available(self, duel: "Duel"):
        phase_correct = duel.phase.phase in [PHASE.MAIN1, PHASE.MAIN2]
        card_correct = self.card.card_type == CARD.MONSTER
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
        player = self.card.belonging
        player.hand.remove(self.card)
        player.allocate_main_monster_zone(self.card)
        self.card.status = CardStatus(position=EXPRESSION_WAY.ATTACK, face=FACE.UP)
        self.card.zone = LOCATION.SELF.MONSTER_ZONE

    def __eq__(self, value):
        if not isinstance(value, NormalSummon):
            return False
        return self.card == value.card

    def __str__(self):
        return f"Normal summon {self.card} to field"


class Skip(Flag):
    def __init__(self, player: "Player", action: Action):
        self.player = player
        self.action = action

    def available(self, duel: "Duel") -> bool:
        return True

    def perform(self, duel: "Duel"):
        super().perform(duel)

    def __str__(self):
        return f"{self.player} skips {self.action}"


class CardNameOnePerTurn(Condition):
    def __init__(self, effect: "Effect"):
        self.effect = effect

    def available(self, duel):
        for action in duel.history.current_turn_actions():
            if isinstance(action, ActivateEffect) and action.effect is self.effect:
                return False
        return True


class TurnChance(Flag):
    def __init__(self, player: "Player"):
        # It's player's turn
        self.player = player

    def __str__(self):
        return f"It's {self.player}'s turn"

    def __eq__(self, value):
        if not isinstance(value, TurnChance):
            return False
        return self.player is value.player


class ActivateEffect(Action):
    def __init__(self, effect: "Effect"):
        self.effect = effect

    def available(self, duel: "Duel") -> bool:
        return self.effect.available(duel)

    def perform(self, duel: "Duel"):
        self.effect.perform(duel)

    def __eq__(self, value):
        if not isinstance(value, ActivateEffect):
            return False
        return self.effect is value.effect


def show_action(actions: list[Action]):
    print("Available actions:")
    for index, action in enumerate(actions):
        logger.info(f"{index}: {action}")
