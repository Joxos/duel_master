from dataclasses import dataclass


from duel.events import DuelState
from phase.models import PhaseWithPlayer
from player.models import Player


@dataclass
class SetPhase(DuelState):
    phase: PhaseWithPlayer


class ShuffleDeck(DuelState): ...


@dataclass
class DrawCard(DuelState):
    player: "Player"
    num: "int"
