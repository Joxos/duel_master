import importlib


def test_sourced_regression_fast_effect_window_transition_open_to_chain_response():
    """Source: https://www.yugioh-card.com/ygo_cms/ygo/all/uploads/FastEffectTiming_for_webpage-1.pdf"""

    timing_module = importlib.import_module("duel_engine.timing")
    fast_effect_module = importlib.import_module("duel_engine.timing.fast_effect")
    FastEffectResolver = timing_module.FastEffectResolver
    SpellSpeed = timing_module.SpellSpeed
    TimingWindow = timing_module.TimingWindow
    FastEffect = fast_effect_module.FastEffect

    resolver = FastEffectResolver()
    effects = (
        FastEffect(effect_id="ss1", controller="p1", spell_speed=SpellSpeed.SS1),
        FastEffect(effect_id="ss2", controller="p1", spell_speed=SpellSpeed.SS2),
        FastEffect(effect_id="ss3", controller="p1", spell_speed=SpellSpeed.SS3),
    )

    open_window = resolver.activatable_effects(
        effects=effects,
        window=TimingWindow.MAIN1_OPEN,
        priority_player="p1",
        is_chain_response=False,
    )
    response_window = resolver.activatable_effects(
        effects=effects,
        window=TimingWindow.MAIN1_OPEN,
        priority_player="p1",
        is_chain_response=True,
    )

    assert [effect.effect_id for effect in open_window] == ["ss1", "ss2", "ss3"]
    assert [effect.effect_id for effect in response_window] == ["ss2", "ss3"]


def test_sourced_regression_damage_step_activation_restrictions_by_substep():
    """Source: https://www.yugioh-card.com/eu/play/damage-step-rules/"""

    battle_module = importlib.import_module("duel_engine.battle")
    DamageStep = battle_module.DamageStep
    DamageStepMachine = battle_module.DamageStepMachine

    machine = DamageStepMachine(current_step=DamageStep.START)
    assert not machine.can_activate("quick")
    assert machine.can_activate("mandatory_trigger")

    machine.advance_step()
    assert machine.current_step == DamageStep.CALC
    assert machine.can_activate("atk_def_modifier")
    assert not machine.can_activate("counter")

    machine.advance_step()
    assert machine.current_step == DamageStep.RESPONSE
    assert machine.can_activate("quick")
    assert machine.can_activate("counter")

    machine.advance_step()
    assert machine.current_step == DamageStep.END
    assert not machine.can_activate("quick")
    assert machine.can_activate("damage_step_trigger")


def test_sourced_regression_psct_conjunction_semantics_then_also_and_if_you_do_and():
    """Source: https://www.yugioh-card.com/en/play/psct/psct-7/"""

    effects_module = importlib.import_module("duel_engine.effects")
    ALSO = effects_module.ALSO
    AND = effects_module.AND
    AND_IF_YOU_DO = effects_module.AND_IF_YOU_DO
    THEN = effects_module.THEN
    Effect = effects_module.Effect
    EffectType = effects_module.EffectType
    resolve = effects_module.resolve

    calls: list[str] = []

    def fail_first(_ctx: object) -> bool:
        calls.append("fail_first")
        return False

    def should_be_blocked(_ctx: object) -> bool:
        calls.append("should_be_blocked")
        return True

    def also_runs(_ctx: object) -> str:
        calls.append("also_runs")
        return "ok"

    def and_runs(_ctx: object) -> bool:
        calls.append("and_runs")
        return True

    effect = Effect(
        effect_type=EffectType.ACTIVATED,
        actions=(
            resolve(fail_first, THEN),
            resolve(should_be_blocked, AND_IF_YOU_DO),
            resolve(also_runs, ALSO),
            resolve(and_runs, AND),
        ),
    )

    results = effect.resolve({})

    assert calls == ["fail_first", "also_runs", "and_runs"]
    assert results == [False, None, "ok", True]
