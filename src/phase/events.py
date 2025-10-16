from dataclasses import dataclass
from typing import TYPE_CHECKING

from duel.events import DuelState

if TYPE_CHECKING:
    from player.models import Player


@dataclass
class TurnChance(DuelState):
    player: "Player"
