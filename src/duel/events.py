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
class DuelStateEvent(Event):
    duel: "Duel"


class DuelStart(DuelStateEvent): ...


class InitialDraw(DuelStateEvent): ...


class SetupCards(DuelStateEvent): ...


@dataclass
class GetAndExecuteUserDecision(DuelStateEvent):
    player: "Player"


@dataclass
class GetAvailableActions(DuelStateEvent):
    player: "Player"


@dataclass
class GetAvailableActivations(DuelStateEvent):
    player: "Player"


@dataclass
class DuelEnd(DuelStateEvent):
    reason: "END_REASON"
    winner: "Player"
