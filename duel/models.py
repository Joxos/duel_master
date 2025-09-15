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
from .actions import Action, NextPhase, NormalSummon, TurnChance, ActivateEffect
from .log import logger
from .actions import SkipOccasion
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
    effects: list[Action]
    conditions: list[Action] = None
    # set in game
    duel: "Duel" = None

    def available(self):
        if self.conditions:
            for condition in self.conditions:
                if not condition.available():
                    return False
        return True

    def __eq__(self, value):
        # Same effect (different cards are allowed)
        if not isinstance(value, Effect):
            return False
        return self.owner.name == value.owner.name and self.index == value.index

    def __str__(self):
        return f"{self.owner.name}'s {self.index} effect."


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
    duel: "Duel" = None
    # set by duel and be used to distinguish cards with same name
    index: int = None
    belonging: "Player" = None

    def __str__(self):
        return f"{self.card_type} {self.name}: {self.race}/{self.attribute}, {self.level}⭐, {self.attack}/{self.defense}, {self.index}/{self.status}/{self.zone}/{self.belonging}"

    def __eq__(self, value):
        # Same card in game
        if not isinstance(value, Card):
            return False
        return self.name == value.name and self.index == value.index


class Player:
    def __init__(
        self, main_deck: list[Card], extra_deck: list[Card], hand: list[Card] = []
    ):
        self.main_deck = main_deck
        self.extra_deck = extra_deck
        self.hand = (
            hand if hand else []
        )  # !!! python uses same default value for all instances of a class so copy empty list to avoid sharing same hands
        self.main_monster_zone: list[Card | None] = [None] * 5
        self.spell_trap_zone: list[Card | None] = [None] * 5
        self.graveyard: list[Card] = []
        self.field_zone: list[Card | None] = [None]
        self.banished: list[Card] = []

        # will be set in game
        self.extra_monster_zone: list[Card | None] = [None] * 2

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

    def previous_after_action(self, action: Action, times: int = 1) -> list[Action]:
        found = 0
        for i in range(len(self.actions) - 1, -1, -1):
            if self.actions[i] == action:
                found += 1
                if found == times:
                    return self.actions[i + 1 :]
        return self.actions

    def previous_after_action_type(self, action_type: type, times: int = 1) -> list[Action]:
        found = 0
        for i in range(len(self.actions) - 1, -1, -1):
            if isinstance(self.actions[i], action_type):
                found += 1
                if found == times:
                    return self.actions[i + 1 :]
        return self.actions

    def current_occasions(self):
        return self.previous_after_action_type(SkipOccasion)

    def current_turn_actions(self):
        return self.previous_after_action_type(TurnChance)

    def last_action(self):
        if self.actions:
            return self.actions[-1]

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
        self.all_cards: list[Card] = []
        self.winner: Player | None = None
        self.actions: list[Action] = []
        self.history: History = History()
        self.chain: list[Effect] = []

        # injection
        self.player_1.extra_monster_zone_1 = self.extra_monster_zone
        self.player_2.extra_monster_zone_2 = self.extra_monster_zone

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
                card.duel = self
                for effect in card.effects:
                    effect.duel = self
                    for condition in effect.conditions:
                        condition.duel = self
                    for effect in effect.effects:
                        effect.duel = self
                self.all_cards.append(card)

        # verbose all_cards
        logger.debug("Verbose all_cards:")
        for card in self.all_cards:
            logger.debug(
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
            self.history.append(TurnChance(self.phase.player))
        logger.info(f"Phase changed to {self.phase}. Turn count: {self.turn_count}")

    def available_actions(self):
        actions = []
        current_player = self.current_player()
        # NextPhase actions
        for to_phase in PHASE.CONSEQUENCE[self.phase.phase]:
            turning = self.phase.phase == PHASE.END and to_phase == PHASE.DRAW
            target_player = (
                self.another_player(current_player) if turning else current_player
            )
            action = NextPhase(
                duel=self,
                owner=current_player,
                _from=PhaseWithPlayer(self.phase.phase, current_player),
                to=PhaseWithPlayer(to_phase, target_player),
            )
            if action.available():
                actions.append(action)
        # NormalSummon action
        for card in self.current_player().hand:
            action = NormalSummon(duel=self, owner=current_player, card=card)
            if action.available():
                actions.append(action)
        # ActivateEffect action
        for card in (
            current_player.hand
            + current_player.field_zone
            + current_player.graveyard
            + current_player.banished
            + current_player.main_monster_zone
            + current_player.spell_trap_zone
        ):
            if isinstance(card, Card):
                for effect in card.effects:
                    if effect.available():
                        actions.append(ActivateEffect(duel=self, owner=current_player, effect=effect))
        # SkipOccasion action
        if not isinstance(self.history.last_action(), SkipOccasion):
            actions.append(SkipOccasion(current_player))
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
