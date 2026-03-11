from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import Enum


class EffectType(Enum):
    ACTIVATED = "activated"
    TRIGGER = "trigger"
    QUICK = "quick"
    IGNITION = "ignition"
    CONTINUOUS = "continuous"


ConditionValue = object
ConditionPredicate = Callable[[object], bool]
CardSelector = Callable[[object], Iterable[object]]
EffectFn = Callable[[object], object]


@dataclass(frozen=True, slots=True)
class Condition:
    field: str
    operator: str
    value: ConditionValue


@dataclass(frozen=True, slots=True)
class Cost:
    payment_type: str
    amount: int


@dataclass(frozen=True, slots=True)
class Target:
    card_selector: CardSelector


class Conjunction(Enum):
    THEN = "THEN"
    ALSO = "ALSO"
    AND_IF_YOU_DO = "AND IF YOU DO"
    AND = "AND"


@dataclass(frozen=True, slots=True)
class Action:
    effect_fn: EffectFn
    conjunction: Conjunction = Conjunction.THEN


__all__ = [
    "Action",
    "CardSelector",
    "Condition",
    "ConditionValue",
    "ConditionPredicate",
    "Conjunction",
    "Cost",
    "EffectFn",
    "EffectType",
    "Target",
]
