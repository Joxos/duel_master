from dataclasses import dataclass
from enumerations import CARD, ATTRIBUTE, SPECIES, PHASE
from events import Event
from typing import Callable
from loguru import logger


@dataclass
class Effect:
    inductions: dict[Event, Callable]


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
    species: SPECIES


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


class Player:
    def __init__(self, main_deck: Deck, extra_deck: Deck):
        self.main_deck = main_deck
        self.extra_deck = extra_deck


class Duel:
    def __init__(self, player_1: Player, player_2: Player):
        self.player_1 = player_1
        self.player_2 = player_2
        self.current_phase = PHASE.START
        self.turn_count = 1
        self.current_player = player_1
        logger.info(
            f"Duel initialized between {player_1} and {player_2}. Starting phase: {self.current_phase}"
        )
