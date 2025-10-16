from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

from cards.enum import ATTRIBUTE, CARD, EXPRESSION_WAY, FACE, RACE

if TYPE_CHECKING:
    from effects.models import Effect
    from field.enum import ZoneType
    from player.models import Player


@dataclass
class Location:
    player: "Player"
    zone: "ZoneType"


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
    effects: Optional[List["Effect"]] = None
    attribute: Optional["ATTRIBUTE"] = None
    attack: Optional[int] = None
    defense: Optional[int] = None
    level: Optional[int] = None
    monster_type: Optional["CARD.MONSTER"] = None
    race: Optional["RACE"] = None
    links: Optional[int] = None
    psacle: Optional[int] = None
    peffects: Optional[List["Effect"]] = None

    # set in game
    status: Optional["CardStatus"] = None
    zone: Optional["ZoneType"] = None
    # set by duel and be used to distinguish cards with same name
    index: Optional[int] = None
    belonging: Optional["Player"] = None

    def __str__(self):
        return f"{self.card_type} {self.name}: {self.race}/{self.attribute}, {self.level}⭐, {self.attack}/{self.defense}, {self.index}/{self.status}/{self.zone}/{self.belonging}"

    def __eq__(self, value):
        # Same card in game
        if not isinstance(value, Card):
            return False
        return self.name == value.name and self.index == value.index
