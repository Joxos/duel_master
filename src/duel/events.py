from dataclasses import dataclass
from typing import TYPE_CHECKING

from moduvent import Event

if TYPE_CHECKING:
    from duel.enum import END_REASON
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


class SetupCards(DuelState): ...


@dataclass
class GetAndExecuteUserDecision(DuelState):
    player: "Player"


@dataclass
class GetAvailableActions(DuelState):
    player: "Player"


@dataclass
class GetAvailableActivations(DuelState):
    player: "Player"


@dataclass
class DuelEnd(DuelState):
    reason: "END_REASON"
    winner: "Player"
