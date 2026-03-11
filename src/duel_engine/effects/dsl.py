from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .types import (
    Action,
    CardSelector,
    Condition,
    ConditionValue,
    Conjunction,
    Cost,
    EffectFn,
    EffectType,
    Target,
)

State = Mapping[str, object]


@dataclass(frozen=True, slots=True)
class Effect:
    effect_type: EffectType
    conditions: tuple[Condition, ...] = ()
    costs: tuple[Cost, ...] = ()
    targets: tuple[Target, ...] = ()
    actions: tuple[Action, ...] = ()

    def can_activate(self, state: State) -> bool:
        return all(
            _evaluate_condition(condition, state) for condition in self.conditions
        )

    def pay_costs(self, state: State) -> bool:
        if not self.costs:
            return True

        resources_obj = state.get("resources", {})
        if not isinstance(resources_obj, dict):
            return False
        resources = resources_obj
        for item in self.costs:
            available = int(resources.get(item.payment_type, 0))
            if available < item.amount:
                return False

        for item in self.costs:
            resources[item.payment_type] = (
                int(resources.get(item.payment_type, 0)) - item.amount
            )
        return True

    def select_targets(self, context: object) -> tuple[object, ...]:
        selected: list[object] = []
        for selection in self.targets:
            selected.extend(tuple(selection.card_selector(context)))
        return tuple(selected)

    def resolve(self, context: object) -> list[object | None]:
        results: list[object | None] = []
        last_success = True

        for item in self.actions:
            conjunction = item.conjunction
            if conjunction == Conjunction.AND_IF_YOU_DO and not last_success:
                results.append(None)
                last_success = False
                continue

            outcome = item.effect_fn(context)
            success = bool(outcome)
            results.append(outcome)

            if conjunction == Conjunction.ALSO:
                last_success = True
            elif conjunction == Conjunction.THEN:
                last_success = success
            elif conjunction == Conjunction.AND_IF_YOU_DO:
                last_success = success
            else:
                last_success = True

        return results


def condition(field: str, operator: str, value: ConditionValue) -> Condition:
    return Condition(field=field, operator=operator, value=value)


def cost(payment_type: str, amount: int) -> Cost:
    if amount < 0:
        raise ValueError("cost amount must be >= 0")
    return Cost(payment_type=payment_type, amount=amount)


def target(card_selector: CardSelector) -> Target:
    return Target(card_selector=card_selector)


def resolve(effect_fn: EffectFn, conjunction: Conjunction = Conjunction.THEN) -> Action:
    return Action(effect_fn=effect_fn, conjunction=conjunction)


THEN = Conjunction.THEN
ALSO = Conjunction.ALSO
AND_IF_YOU_DO = Conjunction.AND_IF_YOU_DO
AND = Conjunction.AND


def _evaluate_condition(item: Condition, state: State) -> bool:
    left = state.get(item.field)
    right = item.value

    if item.operator == "==":
        return left == right
    if item.operator == "!=":
        return left != right
    if item.operator == ">":
        return _is_gt(left, right)
    if item.operator == ">=":
        return _is_ge(left, right)
    if item.operator == "<":
        return _is_lt(left, right)
    if item.operator == "<=":
        return _is_le(left, right)
    if item.operator == "in":
        return left in right if isinstance(right, Iterable) else False
    if item.operator == "contains":
        return right in left if isinstance(left, Iterable) else False

    raise ValueError(f"unsupported condition operator: {item.operator}")


def _is_gt(left: object, right: object) -> bool:
    if isinstance(left, str) and isinstance(right, str):
        return left > right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left > right
    return False


def _is_ge(left: object, right: object) -> bool:
    if isinstance(left, str) and isinstance(right, str):
        return left >= right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left >= right
    return False


def _is_lt(left: object, right: object) -> bool:
    if isinstance(left, str) and isinstance(right, str):
        return left < right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left < right
    return False


def _is_le(left: object, right: object) -> bool:
    if isinstance(left, str) and isinstance(right, str):
        return left <= right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left <= right
    return False


__all__ = [
    "ALSO",
    "AND",
    "AND_IF_YOU_DO",
    "Effect",
    "THEN",
    "condition",
    "cost",
    "resolve",
    "target",
]
