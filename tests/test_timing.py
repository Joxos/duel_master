import pytest

from duel_engine.timing import (
    FastEffectResolver,
    PriorityManager,
    SpellSpeed,
    TimingWindow,
)
from duel_engine.timing.fast_effect import FastEffect


def test_timing_window_enum_contains_required_windows():
    assert {window.name for window in TimingWindow} == {
        "OPEN",
        "DRAW",
        "STANDBY",
        "MAIN1_OPEN",
        "BATTLE_START",
        "DAMAGE",
        "BATTLE_END",
        "MAIN2_OPEN",
        "END_OPEN",
    }


def test_spell_speed_enum_has_three_levels():
    assert SpellSpeed.SS1.value == 1
    assert SpellSpeed.SS2.value == 2
    assert SpellSpeed.SS3.value == 3


def test_priority_manager_alternates_then_closes_on_both_pass():
    manager = PriorityManager(players=("p1", "p2"), current_priority_player="p1")

    assert manager.has_priority("p1")
    assert manager.pass_priority("p1") is False
    assert manager.has_priority("p2")

    assert manager.pass_priority("p2") is True


def test_priority_manager_rejects_non_priority_pass():
    manager = PriorityManager(players=("p1", "p2"), current_priority_player="p1")

    with pytest.raises(ValueError):
        manager.pass_priority("p2")


def test_priority_manager_action_resets_pass_state():
    manager = PriorityManager(players=("p1", "p2"), current_priority_player="p1")

    manager.pass_priority("p1")
    manager.on_action_taken(next_priority_player="p2")

    assert manager.has_priority("p2")
    assert manager.passed_players == set()


def test_fast_effect_resolver_open_window_allows_ss1_ss2_ss3_for_priority_player():
    resolver = FastEffectResolver()
    effects = (
        FastEffect(effect_id="e1", controller="p1", spell_speed=SpellSpeed.SS1),
        FastEffect(effect_id="e2", controller="p1", spell_speed=SpellSpeed.SS2),
        FastEffect(effect_id="e3", controller="p1", spell_speed=SpellSpeed.SS3),
        FastEffect(effect_id="e4", controller="p2", spell_speed=SpellSpeed.SS3),
    )

    activatable = resolver.activatable_effects(
        effects=effects,
        window=TimingWindow.MAIN1_OPEN,
        priority_player="p1",
        is_chain_response=False,
    )

    assert [effect.effect_id for effect in activatable] == ["e1", "e2", "e3"]


def test_fast_effect_resolver_chain_response_blocks_ss1():
    resolver = FastEffectResolver()
    effects = (
        FastEffect(effect_id="e1", controller="p1", spell_speed=SpellSpeed.SS1),
        FastEffect(effect_id="e2", controller="p1", spell_speed=SpellSpeed.SS2),
        FastEffect(effect_id="e3", controller="p1", spell_speed=SpellSpeed.SS3),
    )

    activatable = resolver.activatable_effects(
        effects=effects,
        window=TimingWindow.OPEN,
        priority_player="p1",
        is_chain_response=True,
    )

    assert [effect.effect_id for effect in activatable] == ["e2", "e3"]


def test_fast_effect_resolver_chain_entry_groups_by_spell_speed():
    resolver = FastEffectResolver()
    effects = (
        FastEffect(effect_id="a", controller="p1", spell_speed=SpellSpeed.SS2),
        FastEffect(effect_id="b", controller="p1", spell_speed=SpellSpeed.SS3),
    )

    grouped = resolver.build_chain_candidates(
        effects=effects,
        window=TimingWindow.BATTLE_START,
        priority_player="p1",
        is_chain_response=True,
    )

    assert [effect.effect_id for effect in grouped["SS2"]] == ["a"]
    assert [effect.effect_id for effect in grouped["SS3"]] == ["b"]
    assert grouped["SS1"] == []
