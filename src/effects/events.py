from dataclasses import dataclass

from cards.models import Card
from duel.events import DuelStateEvent


@dataclass
class Activation(DuelStateEvent):
    card: "Card"
    index: int
