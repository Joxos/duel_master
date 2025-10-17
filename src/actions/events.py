from dataclasses import dataclass
from typing import TYPE_CHECKING

from duel.events import DuelStateEvent

if TYPE_CHECKING:
    from cards.models import Card
    from field.models import Location
    from phase.models import PhaseWithPlayer
    from player.models import Player


@dataclass
class SetPhase(DuelStateEvent):
    phase: "PhaseWithPlayer"


class PostPhase(SetPhase): ...


class ShuffleDeck(DuelStateEvent): ...


@dataclass
class DrawCard(DuelStateEvent):
    player: "Player"
    num: int


@dataclass
class NormalSummon(DuelStateEvent):
    player: "Player"
    card: "Card"


@dataclass
class Skip(DuelStateEvent):
    player: "Player"


@dataclass
class MoveCard(DuelStateEvent):
    card: "Card"
    from_zone: "Location"
    to_zone: "Location"
