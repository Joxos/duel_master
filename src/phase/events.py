from dataclasses import dataclass
from typing import TYPE_CHECKING

from duel.events import DuelStateEvent

if TYPE_CHECKING:
    from player.models import Player


@dataclass
class TurnChance(DuelStateEvent):
    next_player: "Player"
