from collections.abc import Iterable

from duel_engine.effects import (
    ALSO,
    AND,
    AND_IF_YOU_DO,
    THEN,
    Effect,
    EffectType,
    condition,
    cost,
    resolve,
    target,
)


def test_condition_cost_target_builders_create_expected_values():
    c = condition("turn_player", "==", "p1")
    k = cost("lp", 1000)

    def select_cards(ctx: object) -> Iterable[object]:
        if not isinstance(ctx, dict):
            return ()
        cards = ctx.get("cards", ())
        return cards if isinstance(cards, Iterable) else ()

    t = target(select_cards)

    assert c.field == "turn_player"
    assert c.operator == "=="
    assert c.value == "p1"
    assert k.payment_type == "lp"
    assert k.amount == 1000
    assert tuple(t.card_selector({"cards": ["c1", "c2"]})) == ("c1", "c2")


def test_effect_can_activate_checks_all_conditions():
    effect = Effect(
        effect_type=EffectType.ACTIVATED,
        conditions=(
            condition("phase", "==", "MAIN1"),
            condition("chain_open", "==", True),
        ),
    )

    assert effect.can_activate({"phase": "MAIN1", "chain_open": True})
    assert not effect.can_activate({"phase": "BATTLE", "chain_open": True})


def test_effect_pay_costs_succeeds_and_deducts_resources():
    effect = Effect(
        effect_type=EffectType.IGNITION,
        costs=(cost("lp", 500), cost("counters", 2)),
    )
    state = {"resources": {"lp": 8000, "counters": 3}}

    assert effect.pay_costs(state)
    assert state["resources"]["lp"] == 7500
    assert state["resources"]["counters"] == 1


def test_effect_pay_costs_fails_without_mutating_state():
    effect = Effect(effect_type=EffectType.IGNITION, costs=(cost("lp", 9000),))
    state = {"resources": {"lp": 8000}}

    assert not effect.pay_costs(state)
    assert state["resources"]["lp"] == 8000


def test_effect_select_targets_flattens_target_selectors():
    def select_allies(ctx: object) -> Iterable[object]:
        if not isinstance(ctx, dict):
            return ()
        allies = ctx.get("allies", ())
        return allies[:1] if isinstance(allies, list) else ()

    def select_enemies(ctx: object) -> Iterable[object]:
        if not isinstance(ctx, dict):
            return ()
        enemies = ctx.get("enemies", ())
        return enemies[:2] if isinstance(enemies, list) else ()

    effect = Effect(
        effect_type=EffectType.QUICK,
        targets=(
            target(select_allies),
            target(select_enemies),
        ),
    )

    chosen = effect.select_targets(
        {
            "allies": ["a1", "a2"],
            "enemies": ["e1", "e2", "e3"],
        }
    )

    assert chosen == ("a1", "e1", "e2")


def test_resolve_then_and_if_you_do_blocks_followup_on_failure():
    calls: list[str] = []

    def draw(_ctx: object) -> bool:
        calls.append("draw")
        return False

    def destroy(_ctx: object) -> bool:
        calls.append("destroy")
        return True

    effect = Effect(
        effect_type=EffectType.ACTIVATED,
        actions=(
            resolve(draw, THEN),
            resolve(destroy, AND_IF_YOU_DO),
        ),
    )

    results = effect.resolve({})

    assert calls == ["draw"]
    assert results == [False, None]


def test_resolve_also_does_not_gate_followup():
    calls: list[str] = []

    def first(_ctx: object) -> bool:
        calls.append("first")
        return False

    def second(_ctx: object) -> str:
        calls.append("second")
        return "ok"

    effect = Effect(
        effect_type=EffectType.ACTIVATED,
        actions=(
            resolve(first, ALSO),
            resolve(second, AND_IF_YOU_DO),
        ),
    )

    results = effect.resolve({})
    assert calls == ["first", "second"]
    assert results == [False, "ok"]


def test_resolve_and_behaves_non_gating_for_followup():
    calls: list[str] = []

    def first(_ctx: object) -> bool:
        calls.append("first")
        return False

    def second(_ctx: object) -> bool:
        calls.append("second")
        return True

    effect = Effect(
        effect_type=EffectType.TRIGGER,
        actions=(
            resolve(first, AND),
            resolve(second, AND_IF_YOU_DO),
        ),
    )

    results = effect.resolve({})
    assert calls == ["first", "second"]
    assert results == [False, True]
