from dataclasses import dataclass
from typing import TYPE_CHECKING

from effects.events import ActivationAvailable

if TYPE_CHECKING:
    from cards.models import Card
    from duel.events import DuelStateEvent
from effects.enum import CHECK_TYPE, UNIT


@dataclass
class Times:
    unit: "UNIT"
    check_type: "CHECK_TYPE"
    counts: int

    def available(self, event: "DuelStateEvent", card: "Card") -> bool:
        duel = event.duel
        scope = []
        if self.unit == UNIT.TURN:
            scope = duel.history.current_turn_actions()
        elif self.unit == UNIT.DUEL:
            scope = duel.history

        counts = 0
        for action in scope:
            if self.check_type == CHECK_TYPE.CARD:
                if isinstance(action, ActivationAvailable) and action.card is card:
                    counts += 1
            elif self.check_type == CHECK_TYPE.NAME:
                if (
                    isinstance(action, ActivationAvailable)
                    and action.card.name == card.name
                ):
                    counts += 1
        return counts < self.counts


class Chain(list): ...
