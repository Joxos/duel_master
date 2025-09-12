from dataclasses import dataclass
from .enumerations import (
    CARD,
    ATTRIBUTE,
    RACE,
    PHASE,
    UNIT,
    CHECK_TYPE,
    CardStatus,
    EXPRESSION_WAY,
    FACE,
    ZoneType,
    LOCATION,
)
from .actions import Action, NextPhase, NormalSummon
from .log import logger
import random


@dataclass
class Times:
    unit: UNIT
    check_type: CHECK_TYPE
    times: int


@dataclass
class Effect:
    owner: "Card"
    index: int
    effect: list[Action]
    conditions: list[Action] = None

    def __eq__(self, value):
        if not isinstance(value, Effect):
            return False
        return self.owner == value.owner and self.index == value.index


@dataclass
class Card:
    name: str
    card_type: CARD

    # optional
    effects: list[Effect] = None
    attribute: ATTRIBUTE = None
    attack: int = None
    defense: int = None
    level: int = None
    monster_type: CARD.MONSTER = None
    race: RACE = None
    links: int = None
    psacle: int = None
    peffects: list[Effect] = None

    # set in game
    status: CardStatus = None
    zone: LOCATION = None
    # set by duel
    index: int = None
    belonging: "Player" = None

    def __str__(self):
        return f"{self.card_type} {self.name}: {self.race}/{self.attribute}, {self.level}⭐, {self.attack}/{self.defense}, {self.index}/{self.status}/{self.zone}/{self.belonging}"


class Player:
    def __init__(
        self, main_deck: list[Card], extra_deck: list[Card], hand: list[Card] = []
    ):
        self.main_deck = main_deck
        self.extra_deck = extra_deck
        self.hand = hand.copy()  # !!! If not copy, hand will be shared with other players since they are all referencing the same list as default value.
        self.main_monster_zone: list[Card | None] = [None] * 5
        self.spell_trap_zone: list[Card | None] = [None] * 5
        self.graveyard: list[Card] = []
        self.field_zone: Card | None = None
        self.banished: list[Card] = []

    def allocate_main_monster_zone(self, card: Card):
        for i in range(5):
            if self.main_monster_zone[i] is None:
                self.main_monster_zone[i] = card
                return i
        return -1

    def __str__(self):
        return f"Player({id(self) % 1000})"

    def __eq__(self, value):
        if not isinstance(value, Player):
            return False
        return id(self) == id(value)


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

    def __str__(self):
        if not self.actions:
            return "Empty history"
        return "\n".join(f"{action}" for i, action in enumerate(self.actions))


class Duel:
    def __init__(self, player_1: Player, player_2: Player):
        self.player_1 = player_1
        self.player_2 = player_2
        self.extra_monster_zone: list[Card | None] = [None] * 2
        self.phase = PhaseWithPlayer(PHASE.DRAW, player_1)
        self.turn_count = 1
        self.occasions: list[Action] = []
        self.all_cards: list[Card] = []
        self.winner: Player | None = None
        self.actions: list[Action] = []
        self.history: History = History()
        self.chain: list[Effect] = []

    def setup(self):
        # cards
        all_decks = [
            (self.player_1.main_deck, ZoneType.DECK, self.player_1),
            (self.player_2.main_deck, ZoneType.DECK, self.player_2),
            (self.player_1.extra_deck, ZoneType.EXTRA_DECK, self.player_1),
            (self.player_2.extra_deck, ZoneType.EXTRA_DECK, self.player_2),
        ]

        index = 0
        for deck, zone_type, belonging in all_decks:
            for card in deck:
                card.index = index
                index += 1
                card.status = CardStatus(EXPRESSION_WAY.NONE, FACE.NONE)
                card.zone = zone_type
                card.belonging = belonging
                self.all_cards.append(card)

        # verbose all_cards
        for card in self.all_cards:
            logger.info(
                f"Card: {card.name}, {card.card_type}, {card.status}, {card.zone}, {card.belonging}"
            )

        random.shuffle(self.player_1.main_deck)
        random.shuffle(self.player_2.main_deck)

    def current_player(self) -> Player:
        return self.phase.player

    def waiting_player(self) -> Player:
        return self.player_1 if self.phase.player == self.player_2 else self.player_2

    def another_player(self, player: Player):
        return self.player_1 if player == self.player_2 else self.player_2

    def next_phase(self, phase: PhaseWithPlayer):
        self.phase = phase
        if self.phase.phase == PHASE.DRAW:
            self.turn_count += 1
            self.phase.player = phase.player
        logger.info(f"Phase changed to {self.phase}. Turn count: {self.turn_count}")

    def available_actions(self):
        actions = []
        # NextPhase actions
        for to_phase in PHASE.CONSEQUENCE[self.phase.phase]:
            turning = self.phase.phase == PHASE.END and to_phase == PHASE.DRAW
            for player in [self.player_1, self.player_2]:
                target_player = self.another_player(player) if turning else player
                action = NextPhase(
                    _from=PhaseWithPlayer(self.phase.phase, player),
                    to=PhaseWithPlayer(to_phase, target_player),
                )
                if action.available(self):
                    actions.append(action)
        # NormalSummon action
        for card in self.current_player().hand:
            action = NormalSummon(card)
            if action.available(self):
                actions.append(action)
        return actions

    def get_card_by_index(self, index: int) -> Card:
        if 0 <= index < len(self.all_cards):
            return self.all_cards[index]
        return None

    def draw_card(self, player: Player, count: int = 1):
        if count > len(player.main_deck):
            self.winner = self.another_player(player)
            return
        for i in range(count):
            card = player.main_deck.pop()
            card.zone = ZoneType.HAND
            player.hand.append(card)
