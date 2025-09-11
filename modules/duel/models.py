from dataclasses import dataclass
from enumerations import CARD, ATTRIBUTE, RACE, PHASE, END_REASON, UNIT, CHECK_TYPE
from occasions import Occasion
from .log import logger
from .actions import NextPhase, Action
from moduvent import event_manager
from .events import NextTurn, PerformAction, DuelEnd, EnterPhase
from typing import Callable
import random



@dataclass
class Times:
    unit: UNIT
    check_type: CHECK_TYPE
    times: int

class Checkable:
    def check(self, duel: "Duel"):
        pass

@dataclass
class Effect:
    times: Times
    conditions: list[Checkable] = None
    effect: Callable[["Duel"], None]

@dataclass
class Card:
    name: str
    card_type: CARD
    effects: list[Effect]


@dataclass
class MonsterCard(Card):
    attribute: ATTRIBUTE
    attack: int
    monster_type: CARD.MONSTER
    race: RACE


@dataclass
class LinkMonsterCard(MonsterCard):
    links: int


@dataclass
class SimpleMonsterCard(MonsterCard):
    level: int
    defense: int


@dataclass
class PendulumMonsterCard(MonsterCard):
    pscale: int
    peffects: list[Effect]


class Deck:
    def __init__(self, cards: list):
        self.cards = cards

    def shuffle(self):
        random.shuffle(self.cards)


class Player:
    def __init__(self, main_deck: Deck, extra_deck: Deck, hand: Deck = Deck([])):
        self.main_deck = main_deck
        self.extra_deck = extra_deck
        self.hand = hand


class Duel:
    def __init__(self, player_1: Player, player_2: Player):
        self.player_1 = player_1
        self.player_2 = player_2
        self.current_phase = PHASE.DRAW
        self.turn_count = 1
        self.current_player = player_1
        self.waiting_player = player_2
        self.occasions: list[Occasion] = []
        logger.info(
            f"Duel initialized between {player_1} and {player_2}. Starting phase: {self.current_phase}"
        )

    def available_phases(self):
        phases = PHASE.CONSEQUENCE[self.current_phase]
        logger.debug(f"Available phases from {self.current_phase}: {phases}")
        return phases

    def next_phase(self, phase: PHASE):
        if phase in PHASE.CONSEQUENCE[self.current_phase]:
            logger.info(f"Phase changing from {self.current_phase} to {phase}")
            self.current_phase = phase
            event_manager.emit(EnterPhase(self, phase))
        else:
            logger.error(
                f"Incorrect phase change attempted: from {self.current_phase} to {phase}"
            )

    def available_actions(self):
        actions = []
        # NextPhase actions
        for phase in PHASE.CONSEQUENCE[self.current_phase]:
            actions.append(NextPhase(_from=self.current_phase, to=phase))
        # Normal Summon action
        logger.debug(f"Available actions in phase {self.current_phase}: {actions}")
        return actions

    def perform_action(self, action: "Action"):
        if isinstance(action, NextPhase):
            logger.info(
                f"Performing action: NextPhase from {action._from} to {action.to}"
            )
            if action.to == PHASE.DRAW:
                event_manager.emit(NextTurn(self, self.waiting_player))
            self.next_phase(action.to)
        else:
            logger.warning(f"Action {action} is not implemented.")
            raise NotImplementedError(f"Action {action} is not implemented.")

    def next_turn(self):
        self.turn_count += 1
        self.current_player, self.waiting_player = (
            self.waiting_player,
            self.current_player,
        )
        logger.info(f"Turn changed: {self.current_player}'s turn.")

    def verbose_state(self):
        state = {
            "current_phase": self.current_phase,
            "turn_count": self.turn_count,
            "current_player": self.current_player,
            "waiting_player": self.waiting_player,
        }
        logger.info(f"Duel state: {state}")

    def show_actions(self, actions: list[Action]):
        print("Available actions:")
        for index, action in enumerate(actions):
            if isinstance(action, NextPhase):
                print(f"{index}: Change phase from {action._from} to {action.to}")

    def show_and_get_action(self):
        logger.info("Prompting player for action.")
        action = None
        while not action:
            actions = self.available_actions()
            self.show_actions(actions)
            try:
                choice = int(input("Choose an action: "))
                action = actions[choice]
                logger.success(f"Player selected action: {action}")
            except (ValueError, IndexError):
                logger.warning("Invalid action choice entered.")
                print("Invalid choice. Please try again.")
        event_manager.emit(PerformAction(self, action))
        logger.debug("PerformAction event emitted.")

    def draw(self, player: Player, count: int = 1):
        for _ in range(count):
            if player.main_deck.cards:
                card = player.main_deck.cards.pop()
                player.hand.cards.append(card)
                logger.info(f"{player} drew card: {card.name}")
            else:
                logger.warning(f"{player}'s main deck is empty. Cannot draw card.")
                self.duel_end(END_REASON.DECK_OUT, self.waiting_player)

    def shuffle_deck(self, player: Player):
        player.main_deck.cards = player.main_deck.cards[:]
        random.shuffle(player.main_deck.cards)
        logger.info(f"{player}'s main deck has been shuffled.")

    def duel_end(self, reason: END_REASON, winner: Player):
        event_manager.emit(DuelEnd(self, reason, winner))

    def initial_draw(self):
        logger.info("Performing initial draw.")
        self.draw(self.player_1, 5)
        self.draw(self.player_2, 5)

    def verbose_deck(self, player: Player):
        logger.info(f"{player}'s Decks:")
        for card in player.main_deck.cards:
            logger.info(f"{card.name}")
