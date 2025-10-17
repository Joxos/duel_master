from dataclasses import dataclass

from cards.models import Card
from duel.events import DuelStateEvent
from player.models import Player


@dataclass
class ActivationAvailable(DuelStateEvent):
    player: "Player"
    card: "Card"
    index: int


class Activate(ActivationAvailable): ...


class Activation(ActivationAvailable): ...
