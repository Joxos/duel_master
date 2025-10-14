from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional


if TYPE_CHECKING:
    from cards.effects.actions.models import Action
    from cards.effects.enumerations import CHECK_TYPE, UNIT
    from cards.models import Card


@dataclass
class Times:
    unit: "UNIT"
    check_type: "CHECK_TYPE"
    times: "int"


@dataclass
class Effect:
    owner: "Card"
    index: int
    effects: List["Action"]
    conditions: Optional[List["Action"]] = None

    def available(self):
        if self.conditions:
            for condition in self.conditions:
                if not all(condition, condition.available()):
                    return False
        return True

    def __eq__(self, value):
        # Same effect (different cards are allowed)
        if not isinstance(value, Effect):
            return False
        return self.owner.name == value.owner.name and self.index == value.index

    def __str__(self):
        return f"{self.owner.name}'s {self.index} effect."
