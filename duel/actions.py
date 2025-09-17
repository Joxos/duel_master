from .enumerations import PHASE, CARD, CardStatus, LOCATION, EXPRESSION_WAY, FACE
from typing import TYPE_CHECKING
from .log import logger

if TYPE_CHECKING:
    from .models import Duel, PhaseWithPlayer, Card, Player, Effect


class Flag:
    def __init__(self):
        pass


class Condition(Flag):
    def __init__(self, duel: "Duel" = None):
        self.duel = duel

    def available(self) -> bool:
        return False


class Action(Condition):
    def __init__(self, owner: "Player", duel: "Duel" = None):
        super().__init__(duel=duel)
        self.owner = owner

    def available(self) -> bool:
        return super().available()

    def perform(self):
        self.duel.history.append(self)


class NextPhase(Action):
    def __init__(
        self,
        owner: "Player",
        _from: "PhaseWithPlayer",
        to: "PhaseWithPlayer",
        duel: "Duel" = None,
    ):
        super().__init__(owner=owner, duel=duel)
        self._from = _from
        self.to = to

    def available(self) -> bool:
        initial_phase_correct = self.duel.phase == self._from
        consequence = (
            PHASE.CONSEQUENCE
            if self.duel.turn_count > 1
            else PHASE.CONSEQUENCE_OF_TURN_1
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

    def perform(self):
        super().perform()
        self.duel.next_phase(self.to)

    def __eq__(self, value):
        if not isinstance(value, NextPhase):
            return False
        return self._from == value._from and self.to == value.to

    def __str__(self):
        return f"Change phase from {self._from} to {self.to}"


class NormalSummon(Action):
    def __init__(self, owner: "Player", card: "Card", duel: "Duel" = None):
        super().__init__(owner=owner, duel=duel)
        self.card = card

    def available(self):
        phase_correct = self.duel.phase.phase in [PHASE.MAIN1, PHASE.MAIN2]
        card_correct = self.card.card_type == CARD.MONSTER
        level_correct = self.card.level <= 4
        if phase_correct and card_correct and level_correct:
            return True
        else:
            logger.debug(
                f"NormalSummon not available: {self.card} with phase_correct: {phase_correct}, card_correct: {card_correct}, level_correct: {level_correct}"
            )
            return False

    def perform(self):
        super().perform()
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


class SkipOccasion(Action):
    def __init__(self, owner: "Player", duel: "Duel" = None):
        super().__init__(owner=owner, duel=duel)

    def available(self) -> bool:
        # TODO: implement this
        return True

    def perform(self):
        super().perform()

    def __str__(self):
        return f"{self.owner} skips."


class CardNameOnePerTurn(Condition):
    def __init__(self, effect: "Effect", duel: "Duel" = None):
        super().__init__(duel=duel)
        self.effect = effect

    def available(self):
        for action in self.duel.history.current_turn_actions():
            if isinstance(action, ActivateEffect) and action.effect == self.effect:
                return False
        return True


class CardOnePerTurn(Condition):
    def __init__(self, effect: "Effect", duel: "Duel" = None):
        super().__init__(duel=duel)
        self.effect = effect

    def available(self):
        for action in self.duel.history.current_turn_actions():
            if (
                isinstance(action, ActivateEffect)
                and action.effect.owner == self.effect.owner
            ):
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
    def __init__(self, owner: "Player", effect: "Effect", duel: "Duel" = None):
        super().__init__(owner=owner, duel=duel)
        self.effect = effect

    def available(self) -> bool:
        return self.effect.available(self.duel)

    def perform(self):
        self.duel.chain.append(self.effect)

    def __eq__(self, value):
        if not isinstance(value, ActivateEffect):
            return False
        return self.effect is value.effect

    def __str__(self):
        return f"Activate {self.effect}"


class CardNormalSummonOccasion(Condition):
    def __init__(self, card: "Card", duel: "Duel" = None):
        super().__init__(duel=duel)
        self.card = card

    def available(self):
        for action in self.duel.history.current_occasions():
            if isinstance(action, NormalSummon) and action.card == self.card:
                return True
        return False


def show_action(actions: list[Action]):
    print("Available actions:")
    for index, action in enumerate(actions):
        logger.info(f"{index}: {action}")
