from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Dict, Optional

from cards.enum import ATTRIBUTE, CARD, EXPRESSION_WAY, FACE, NAME_FIELD, RACE
from field.models import Location

if TYPE_CHECKING:
    from player.models import Player


@dataclass
class CardStatus:
    position: EXPRESSION_WAY
    face: FACE

    def __eq__(self, value):
        if not isinstance(value, CardStatus):
            return False
        return self.position == value.position and self.face == value.face


@dataclass
class Card:
    name: str
    card_type: CARD.MONSTER | CARD.SPELL | CARD.TRAP

    # optional
    attribute: Optional["ATTRIBUTE"] = None
    effects: Optional[Dict[int, Callable]] = None  # effect_index: effect_func
    attack: Optional[int] = None
    defense: Optional[int] = None
    level: Optional[int] = None
    monster_type: Optional["CARD.MONSTER"] = None
    race: Optional["RACE"] = None
    links: Optional[int] = None
    psacle: Optional[int] = None
    name_field: Optional[NAME_FIELD] = None

    # set in game
    status: Optional["CardStatus"] = None
    zone: Optional["Location"] = None
    # set by duel and be used to distinguish cards with same name
    index: Optional[int] = None
    belonging: Optional["Player"] = None

    def __str__(self):
        return f"{self.card_type} {self.name}: {self.race}/{self.attribute}, {self.level}⭐, {self.attack}/{self.defense}, {self.index}/{self.status}/{self.zone}/{self.belonging}"

    def __eq__(self, value):
        return self is value
