from typing import cast

from pydantic import Field

from duel_core.models import MutableModel
from duel_core.mr2020.models.card import Card, RuntimeCard


class Zone(MutableModel):
    card: RuntimeCard | None = None


class Deck(MutableModel):
    cards: list[Card | RuntimeCard] = Field(default_factory=list)

    def draw(self, num: int) -> list[RuntimeCard]:
        drawn = self.cards[:num]
        del self.cards[:num]
        return cast(list[RuntimeCard], drawn)


class Player(MutableModel):
    label: str
    main_deck: Deck
    extra_deck: Deck = Field(default_factory=Deck)
    hand: list[RuntimeCard] = Field(default_factory=list)
    monster_zones: list[Zone] = Field(default_factory=lambda: [Zone()])
    graveyard: list[RuntimeCard] = Field(default_factory=list)
    life_points: int = 0
