from dataclasses import dataclass
from .enumerations import (
    CARD,
    ATTRIBUTE,
    RACE,
    PHASE,
    UNIT,
    CHECK_TYPE,
    CardStatus,
    POSITION,
    FACE,
)
from .occasions import Occasion
from .actions import Action, NextPhase
from .log import logger
import random


@dataclass
class Times:
    unit: UNIT
    check_type: CHECK_TYPE
    times: int


@dataclass
class Effect:
    effect: list[Action]
    conditions: list[Action] = None


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


@dataclass
class CardInPlay:
    card: Card
    status: CardStatus


class Player:
    def __init__(
        self, main_deck: list[Card], extra_deck: list[Card], hand: list[Card] = []
    ):
        self.main_deck = main_deck
        self.extra_deck = extra_deck
        self.hand = hand
        self.main_monster_zone: list[CardInPlay | None] = [None] * 5
        self.spell_trap_zone: list[CardInPlay | None] = [None] * 5
        self.graveyard: list[CardInPlay] = []
        self.field_zone: CardInPlay | None = None
        self.banished: list[CardInPlay] = []

    def __str__(self):
        return f"Player({id(self) % 1000})"


class PhaseWithPlayer:
    def __init__(self, phase: PHASE, player: Player):
        self.phase = phase
        self.player = player

    def __eq__(self, value):
        if not isinstance(value, PhaseWithPlayer):
            return False
        return self.phase == value.phase and self.player == value.player

    def __str__(self):
        return f"Phase: {self.phase}, Player: {self.player}"


class History:
    def __init__(self):
        self.actions: list[Action] = []

    def append(self, action: Action):
        self.actions.append(action)

    def previous_after(self, action: Action, times: int = 1) -> list[Action]:
        # findd action from last to previous for times
        found = 0
        for i in range(len(self.actions) - 1, -1, -1):
            if self.actions[i] == action:
                found += 1
                if found == times:
                    return self.actions[i + 1 :]
        return []


class Duel:
    def __init__(self, player_1: Player, player_2: Player):
        self.player_1 = player_1
        self.player_2 = player_2
        self.phase = PhaseWithPlayer(PHASE.DRAW, player_1)
        self.turn_count = 1
        self.occasions: list[Occasion] = []
        self.all_cards: list[CardInPlay] = []
        self.winner: Player | None = None
        self.actions: list[Action] = []
        self.history: History = History()
        self.chain: list[Effect] = []

    def setup(self):
        # actions
        # NextPhase actions
        for from_phase in PHASE.CONSEQUENCE:
            for to_phase in PHASE.CONSEQUENCE[from_phase]:
                if from_phase == PHASE.END and to_phase == PHASE.DRAW:
                    self.actions.append(
                        NextPhase(
                            _from=PhaseWithPlayer(from_phase, self.player_1),
                            to=PhaseWithPlayer(to_phase, self.player_2),
                        )
                    )
                    self.actions.append(
                        NextPhase(
                            _from=PhaseWithPlayer(from_phase, self.player_2),
                            to=PhaseWithPlayer(to_phase, self.player_1),
                        )
                    )
                else:
                    self.actions.append(
                        NextPhase(
                            _from=PhaseWithPlayer(from_phase, self.player_1),
                            to=PhaseWithPlayer(to_phase, self.player_1),
                        )
                    )
                    self.actions.append(
                        NextPhase(
                            _from=PhaseWithPlayer(from_phase, self.player_2),
                            to=PhaseWithPlayer(to_phase, self.player_2),
                        )
                    )
        # verbose self.actions
        for action in self.actions:
            if isinstance(action, NextPhase):
                logger.info(f"NextPhase from {action._from} to {action.to}")

        # cards
        for card in (
            self.player_1.main_deck
            + self.player_1.extra_deck
            + self.player_2.main_deck
            + self.player_2.extra_deck
        ):
            self.all_cards.append(
                CardInPlay(
                    card=card, status=CardStatus(position=POSITION.NONE, face=FACE.NONE)
                )
            )

        random.shuffle(self.player_1.main_deck)
        random.shuffle(self.player_2.main_deck)

    def current_player(self) -> Player:
        return self.phase.player

    def waiting_player(self) -> Player:
        return self.player_1 if self.phase.player == self.player_2 else self.player_2

    def next_phase(self, phase: PhaseWithPlayer):
        self.phase = phase
        if self.phase.phase == PHASE.DRAW:
            self.turn_count += 1
            self.phase.player = phase.player
        logger.info(f"Phase changed to {self.phase}. Turn count: {self.turn_count}")

    def available_actions(self):
        actions = []
        for action in self.actions:
            if action.available(self):
                actions.append(action)
        return actions

    # def available_phases(self):
    #     phases = PHASE.CONSEQUENCE[self.phase]
    #     logger.debug(f"Available phases from {self.phase}: {phases}")
    #     return phases

    # def next_phase(self, phase: PHASE):
    #     if phase in PHASE.CONSEQUENCE[self.phase]:
    #         logger.info(f"Phase changing from {self.phase} to {phase}")
    #         self.phase = phase
    #         event_manager.emit(EnterPhase(self, phase))
    #     else:
    #         logger.error(
    #             f"Incorrect phase change attempted: from {self.phase} to {phase}"
    #         )

    # def available_actions(self):
    #     actions = []
    #     # NextPhase actions
    #     for phase in PHASE.CONSEQUENCE[self.phase]:
    #         actions.append(NextPhase(_from=self.phase, to=phase))
    #     # Normal Summon action
    #     logger.debug(f"Available actions in phase {self.phase}: {actions}")
    #     return actions

    # def perform_action(self, action: "Action"):
    #     if isinstance(action, NextPhase):
    #         logger.info(
    #             f"Performing action: NextPhase from {action._from} to {action.to}"
    #         )
    #         if action.to == PHASE.DRAW:
    #             event_manager.emit(NextTurn(self, self.waiting_player))
    #         self.next_phase(action.to)
    #     else:
    #         logger.warning(f"Action {action} is not implemented.")
    #         raise NotImplementedError(f"Action {action} is not implemented.")

    # def next_turn(self):
    #     self.turn_count += 1
    #     self.current_player, self.waiting_player = (
    #         self.waiting_player,
    #         self.current_player,
    #     )
    #     logger.info(f"Turn changed: {self.current_player}'s turn.")

    # def verbose_state(self):
    #     state = {
    #         "current_phase": self.phase,
    #         "turn_count": self.turn_count,
    #         "current_player": self.current_player,
    #         "waiting_player": self.waiting_player,
    #     }
    #     logger.info(f"Duel state: {state}")

    # def show_actions(self, actions: list[Action]):
    #     print("Available actions:")
    #     for index, action in enumerate(actions):
    #         if isinstance(action, NextPhase):
    #             print(f"{index}: Change phase from {action._from} to {action.to}")

    # def show_and_get_action(self):
    #     logger.info("Prompting player for action.")
    #     action = None
    #     while not action:
    #         actions = self.available_actions()
    #         self.show_actions(actions)
    #         try:
    #             choice = int(input("Choose an action: "))
    #             action = actions[choice]
    #             logger.success(f"Player selected action: {action}")
    #         except (ValueError, IndexError):
    #             logger.warning("Invalid action choice entered.")
    #             print("Invalid choice. Please try again.")
    #     event_manager.emit(PerformAction(self, action))
    #     logger.debug("PerformAction event emitted.")

    # def draw(self, player: Player, count: int = 1):
    #     for _ in range(count):
    #         if player.main_deck.cards:
    #             card = player.main_deck.cards.pop()
    #             player.hand.cards.append(card)
    #             logger.info(f"{player} drew card: {card.name}")
    #         else:
    #             logger.warning(f"{player}'s main deck is empty. Cannot draw card.")
    #             self.duel_end(END_REASON.DECK_OUT, self.waiting_player)

    # def shuffle_deck(self, player: Player):
    #     player.main_deck.cards = player.main_deck.cards[:]
    #     random.shuffle(player.main_deck.cards)
    #     logger.info(f"{player}'s main deck has been shuffled.")

    # def duel_end(self, reason: END_REASON, winner: Player):
    #     event_manager.emit(DuelEnd(self, reason, winner))

    # def initial_draw(self):
    #     logger.info("Performing initial draw.")
    #     self.draw(self.player_1, 5)
    #     self.draw(self.player_2, 5)

    # def verbose_deck(self, player: Player):
    #     logger.info(f"{player}'s Decks:")
    #     for card in player.main_deck.cards:
    #         logger.info(f"{card.name}")
