from dataclasses import dataclass
from typing import TYPE_CHECKING

from moduvent import Event

from duel.enumerations import END_REASON

if TYPE_CHECKING:
    from duel.models import Duel
    from player.models import Player


@dataclass
class DuelInit(Event):
    player_1: "Player"
    player_2: "Player"


@dataclass
class DuelState(Event):
    duel: "Duel"


class DuelStart(DuelState): ...


class InitialDraw(DuelState): ...


@dataclass
class DuelEnd(DuelState):
    reason: END_REASON
    winner: "Player"
