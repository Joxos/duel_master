from __future__ import annotations

from typing import Any

from duel_engine.effects import (
    CHESHIRE_CAT_ID,
    DORMOUSE_ID,
    IN_UNDERGROUND_ID,
    MARCH_HARE_ID,
    MTP07_ID,
    WHITE_RABBIT_ID,
    cheshire_cat_main_phase_banish_self_draw_two,
    dormouse_main_phase_exclude_from_deck_and_atk_boost,
    in_underground_activation_optional_exclude,
    march_hare_quick_exclude_and_ss_from_hand,
    mtp07_trap_activation_search_monster,
    p3_banish_trigger_pay_lp_and_ss,
    white_rabbit_trigger_set_trap,
)
from duel_engine.timing import SpellSpeed, TimingWindow


def _state() -> dict[str, Any]:
    return {
        "decks": {
            "p1": [MTP07_ID, DORMOUSE_ID, MARCH_HARE_ID, WHITE_RABBIT_ID],
            "p2": [],
        },
        "hands": {
            "p1": [CHESHIRE_CAT_ID, MARCH_HARE_ID, WHITE_RABBIT_ID],
            "p2": [],
        },
        "monsters": {
            "p1": [DORMOUSE_ID],
            "p2": ["OPP-MONSTER"],
        },
        "banished": {"p1": [], "p2": []},
        "graveyards": {"p1": [], "p2": []},
        "set_traps": {"p1": [], "p2": []},
        "set_this_turn": {"p1": [], "p2": []},
        "atk_boosts": {"p1": {}, "p2": {}},
        "field_spell": {"p1": None, "p2": None},
        "lp": {"p1": 8000, "p2": 8000},
        "trigger": {},
    }


def test_white_rabbit_trigger_sets_mtp07_from_deck():
    state = _state()
    state["trigger"] = {
        "event": "summon",
        "card_id": WHITE_RABBIT_ID,
        "controller": "p1",
    }

    activated = white_rabbit_trigger_set_trap(state, controller="p1")

    assert activated
    assert MTP07_ID not in state["decks"]["p1"]
    assert state["set_traps"]["p1"] == [MTP07_ID]


def test_cheshire_cat_main_phase_banish_self_draw_two_requires_open_priority():
    state = _state()

    assert not cheshire_cat_main_phase_banish_self_draw_two(
        state,
        controller="p1",
        turn_player="p2",
        priority_player="p1",
        window=TimingWindow.MAIN1_OPEN,
        is_chain_response=False,
    )

    activated = cheshire_cat_main_phase_banish_self_draw_two(
        state,
        controller="p1",
        turn_player="p1",
        priority_player="p1",
        window=TimingWindow.MAIN1_OPEN,
        is_chain_response=False,
    )

    assert activated
    assert CHESHIRE_CAT_ID in state["banished"]["p1"]
    assert len(state["hands"]["p1"]) == 4


def test_march_hare_quick_effect_respects_fast_effect_timing_and_chain_speed():
    state = _state()
    state["hands"]["p1"] = [MARCH_HARE_ID, WHITE_RABBIT_ID]

    assert march_hare_quick_exclude_and_ss_from_hand(
        state,
        controller="p1",
        priority_player="p1",
        window=TimingWindow.BATTLE_START,
        is_chain_response=True,
        cost_card_id=WHITE_RABBIT_ID,
        summon_card_id=MARCH_HARE_ID,
        chain_top_spell_speed=SpellSpeed.SS2,
    )

    assert WHITE_RABBIT_ID in state["banished"]["p1"]
    assert MARCH_HARE_ID in state["monsters"]["p1"]

    state2 = _state()
    state2["hands"]["p1"] = [MARCH_HARE_ID, WHITE_RABBIT_ID]
    assert not march_hare_quick_exclude_and_ss_from_hand(
        state2,
        controller="p1",
        priority_player="p1",
        window=TimingWindow.BATTLE_START,
        is_chain_response=True,
        cost_card_id=WHITE_RABBIT_ID,
        summon_card_id=MARCH_HARE_ID,
        chain_top_spell_speed=SpellSpeed.SS3,
    )


def test_dormouse_main_phase_banish_from_deck_and_apply_atk_boost():
    state = _state()

    activated = dormouse_main_phase_exclude_from_deck_and_atk_boost(
        state,
        controller="p1",
        turn_player="p1",
        priority_player="p1",
        window=TimingWindow.MAIN1_OPEN,
        is_chain_response=False,
        deck_banish_card_id=WHITE_RABBIT_ID,
        target_monster_id=DORMOUSE_ID,
        boost_amount=500,
    )

    assert activated
    assert WHITE_RABBIT_ID in state["banished"]["p1"]
    assert state["atk_boosts"]["p1"][DORMOUSE_ID] == 500


def test_p3_banish_trigger_pays_lp_and_special_summons():
    state = _state()
    state["banished"]["p1"] = [WHITE_RABBIT_ID]
    state["trigger"] = {
        "event": "banished",
        "card_id": WHITE_RABBIT_ID,
        "controller": "p1",
    }

    activated = p3_banish_trigger_pay_lp_and_ss(
        state,
        controller="p1",
        card_id=WHITE_RABBIT_ID,
        lp_cost=300,
    )

    assert activated
    assert state["lp"]["p1"] == 7700
    assert WHITE_RABBIT_ID in state["monsters"]["p1"]


def test_in_underground_activation_optional_exclude():
    state = _state()
    state["hands"]["p1"] = [WHITE_RABBIT_ID]

    assert in_underground_activation_optional_exclude(
        state,
        controller="p1",
        turn_player="p1",
        priority_player="p1",
        window=TimingWindow.MAIN1_OPEN,
        is_chain_response=False,
        optional_exclude_card_id=WHITE_RABBIT_ID,
    )
    assert state["field_spell"]["p1"] == IN_UNDERGROUND_ID
    assert WHITE_RABBIT_ID in state["banished"]["p1"]

    state2 = _state()
    assert in_underground_activation_optional_exclude(
        state2,
        controller="p1",
        turn_player="p1",
        priority_player="p1",
        window=TimingWindow.MAIN1_OPEN,
        is_chain_response=False,
        optional_exclude_card_id=None,
    )
    assert state2["field_spell"]["p1"] == IN_UNDERGROUND_ID
    assert state2["banished"]["p1"] == []


def test_mtp07_trap_activation_searches_maliss_monster_and_set_turn_blocked():
    state = _state()
    state["set_traps"]["p1"] = [MTP07_ID]

    activated = mtp07_trap_activation_search_monster(
        state,
        controller="p1",
        priority_player="p1",
        window=TimingWindow.BATTLE_START,
        is_chain_response=True,
        chain_top_spell_speed=SpellSpeed.SS2,
    )

    assert activated
    assert MTP07_ID in state["graveyards"]["p1"]
    assert any(card.startswith("MALISS-P-") for card in state["hands"]["p1"])

    state2 = _state()
    state2["set_traps"]["p1"] = [MTP07_ID]
    state2["set_this_turn"]["p1"] = [MTP07_ID]
    assert not mtp07_trap_activation_search_monster(
        state2,
        controller="p1",
        priority_player="p1",
        window=TimingWindow.BATTLE_START,
        is_chain_response=True,
    )
