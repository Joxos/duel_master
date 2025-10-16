from dataclasses import dataclass
from typing import TYPE_CHECKING

from duel.events import DuelState

if TYPE_CHECKING:
    from cards.models import Card
    from phase.models import PhaseWithPlayer
    from player.models import Player


@dataclass
class SetPhase(DuelState):
    phase: "PhaseWithPlayer"


class PostPhase(SetPhase): ...


class ShuffleDeck(DuelState): ...


@dataclass
class DrawCard(DuelState):
    player: "Player"
    num: int


@dataclass
class NormalSummon(DuelState):
    player: "Player"
    card: "Card"


@dataclass
class Skip(DuelState):
    player: "Player"
