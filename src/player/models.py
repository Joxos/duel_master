from typing import TYPE_CHECKING, List, Optional, Sequence, MutableSequence

from field.models import Field

if TYPE_CHECKING:
    from utils import C
    from cards.models import Card


class Player:
    def __init__(
        self,
        name: str,
        main_deck: List["Card"],
        extra_deck: List["Card"],
        hand: Optional[List["Card"]] = None,
    ):
        self.name = name
        if hand is None:
            hand = []
        self.field = Field(main_deck=main_deck, extra_deck=extra_deck, hands=hand)

    def __eq__(self, value: object) -> bool:
        return self is value
