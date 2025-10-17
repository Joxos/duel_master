from dataclasses import dataclass
from typing import TYPE_CHECKING

from duel.events import DuelStateEvent

if TYPE_CHECKING:
    from cards.models import Card
    from field.models import Location
    from phase.models import PhaseWithPlayer
    from player.models import Player


class Action(DuelStateEvent):
    """Base class for all actions."""


@dataclass
class SetPhase(Action):
    phase: "PhaseWithPlayer"


class PostPhase(SetPhase): ...


class ShuffleDeck(Action): ...


@dataclass
class DrawCard(Action):
    player: "Player"
    num: int


@dataclass
class NormalSummon(Action):
    player: "Player"
    card: "Card"

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, NormalSummon):
            return False
        return self.player is value.player and self.card is value.card


@dataclass
class Skip(Action):
    player: "Player"


@dataclass
class MoveCard(Action):
    card: "Card"
    from_zone: "Location"
    to_zone: "Location"
