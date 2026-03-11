from __future__ import annotations

from collections.abc import MutableMapping
from typing import cast

from duel_engine.timing import FastEffectResolver, SpellSpeed, TimingWindow
from duel_engine.timing.fast_effect import FastEffect

WHITE_RABBIT_ID = "MALISS-P-WHITE-RABBIT"
CHESHIRE_CAT_ID = "MALISS-P-CHESHIRE-CAT"
MARCH_HARE_ID = "MALISS-P-MARCH-HARE"
DORMOUSE_ID = "MALISS-P-DORMOUSE"
IN_UNDERGROUND_ID = "MALISS-IN-UNDERGROUND"
MTP07_ID = "MALISS-C-MTP-07"


def white_rabbit_trigger_set_trap(
    state: MutableMapping[str, object],
    *,
    controller: str,
) -> bool:
    trigger = _as_dict(state.get("trigger"))
    if trigger.get("event") != "summon":
        return False
    if trigger.get("card_id") != WHITE_RABBIT_ID:
        return False
    if trigger.get("controller") != controller:
        return False

    deck = _zone(state, "decks", controller)
    set_traps = _zone(state, "set_traps", controller)
    if len(set_traps) >= 5:
        return False
    if MTP07_ID not in deck:
        return False

    deck.remove(MTP07_ID)
    set_traps.append(MTP07_ID)
    return True


def cheshire_cat_main_phase_banish_self_draw_two(
    state: MutableMapping[str, object],
    *,
    controller: str,
    turn_player: str,
    priority_player: str,
    window: TimingWindow,
    is_chain_response: bool,
) -> bool:
    if not _can_activate_ignition(
        controller=controller,
        turn_player=turn_player,
        priority_player=priority_player,
        window=window,
        is_chain_response=is_chain_response,
    ):
        return False

    hand = _zone(state, "hands", controller)
    if CHESHIRE_CAT_ID not in hand:
        return False

    hand.remove(CHESHIRE_CAT_ID)
    _zone(state, "banished", controller).append(CHESHIRE_CAT_ID)
    _draw(state, controller=controller, count=2)
    return True


def march_hare_quick_exclude_and_ss_from_hand(
    state: MutableMapping[str, object],
    *,
    controller: str,
    priority_player: str,
    window: TimingWindow,
    is_chain_response: bool,
    cost_card_id: str,
    summon_card_id: str,
    chain_top_spell_speed: SpellSpeed | int | None = None,
) -> bool:
    if not _can_activate_fast(
        controller=controller,
        priority_player=priority_player,
        window=window,
        is_chain_response=is_chain_response,
        spell_speed=SpellSpeed.SS2,
        chain_top_spell_speed=chain_top_spell_speed,
    ):
        return False

    hand = _zone(state, "hands", controller)
    if cost_card_id == summon_card_id:
        return False
    if cost_card_id not in hand or summon_card_id not in hand:
        return False

    hand.remove(cost_card_id)
    _zone(state, "banished", controller).append(cost_card_id)
    hand.remove(summon_card_id)
    _zone(state, "monsters", controller).append(summon_card_id)
    return True


def dormouse_main_phase_exclude_from_deck_and_atk_boost(
    state: MutableMapping[str, object],
    *,
    controller: str,
    turn_player: str,
    priority_player: str,
    window: TimingWindow,
    is_chain_response: bool,
    deck_banish_card_id: str,
    target_monster_id: str,
    boost_amount: int = 300,
) -> bool:
    if not _can_activate_ignition(
        controller=controller,
        turn_player=turn_player,
        priority_player=priority_player,
        window=window,
        is_chain_response=is_chain_response,
    ):
        return False

    deck = _zone(state, "decks", controller)
    monsters = _zone(state, "monsters", controller)
    if deck_banish_card_id not in deck:
        return False
    if target_monster_id not in monsters:
        return False

    deck.remove(deck_banish_card_id)
    _zone(state, "banished", controller).append(deck_banish_card_id)
    atk_boosts = _player_nested_map(state, "atk_boosts", controller)
    existing_boost = _to_int(atk_boosts.get(target_monster_id), default=0)
    atk_boosts[target_monster_id] = existing_boost + boost_amount
    return True


def p3_banish_trigger_pay_lp_and_ss(
    state: MutableMapping[str, object],
    *,
    controller: str,
    card_id: str,
    lp_cost: int = 300,
) -> bool:
    trigger = _as_dict(state.get("trigger"))
    if trigger.get("event") != "banished":
        return False
    if trigger.get("card_id") != card_id:
        return False
    if trigger.get("controller") != controller:
        return False

    lp_by_player = _player_scalar_map(state, "lp")
    current_lp = _to_int(lp_by_player.get(controller), default=0)
    if current_lp < lp_cost:
        return False

    banished = _zone(state, "banished", controller)
    if card_id not in banished:
        return False

    banished.remove(card_id)
    _zone(state, "monsters", controller).append(card_id)
    lp_by_player[controller] = current_lp - lp_cost
    return True


def in_underground_activation_optional_exclude(
    state: MutableMapping[str, object],
    *,
    controller: str,
    turn_player: str,
    priority_player: str,
    window: TimingWindow,
    is_chain_response: bool,
    optional_exclude_card_id: str | None,
) -> bool:
    if not _can_activate_ignition(
        controller=controller,
        turn_player=turn_player,
        priority_player=priority_player,
        window=window,
        is_chain_response=is_chain_response,
    ):
        return False

    if optional_exclude_card_id is not None:
        hand = _zone(state, "hands", controller)
        if optional_exclude_card_id not in hand:
            return False

    field_spell = _player_scalar_map(state, "field_spell")
    field_spell[controller] = IN_UNDERGROUND_ID

    if optional_exclude_card_id is not None:
        hand = _zone(state, "hands", controller)
        hand.remove(optional_exclude_card_id)
        _zone(state, "banished", controller).append(optional_exclude_card_id)

    return True


def mtp07_trap_activation_search_monster(
    state: MutableMapping[str, object],
    *,
    controller: str,
    priority_player: str,
    window: TimingWindow,
    is_chain_response: bool,
    chain_top_spell_speed: SpellSpeed | int | None = None,
) -> bool:
    if not _can_activate_fast(
        controller=controller,
        priority_player=priority_player,
        window=window,
        is_chain_response=is_chain_response,
        spell_speed=SpellSpeed.SS2,
        chain_top_spell_speed=chain_top_spell_speed,
    ):
        return False

    set_traps = _zone(state, "set_traps", controller)
    if MTP07_ID not in set_traps:
        return False

    set_this_turn = _zone(state, "set_this_turn", controller)
    if MTP07_ID in set_this_turn:
        return False

    deck = _zone(state, "decks", controller)
    search_target = next((cid for cid in deck if cid.startswith("MALISS-P-")), None)
    if search_target is None:
        return False

    set_traps.remove(MTP07_ID)
    _zone(state, "graveyards", controller).append(MTP07_ID)
    deck.remove(search_target)
    _zone(state, "hands", controller).append(search_target)
    return True


def _can_activate_ignition(
    *,
    controller: str,
    turn_player: str,
    priority_player: str,
    window: TimingWindow,
    is_chain_response: bool,
) -> bool:
    if controller != turn_player:
        return False
    if controller != priority_player:
        return False
    if is_chain_response:
        return False
    return window in {TimingWindow.MAIN1_OPEN, TimingWindow.MAIN2_OPEN}


def _can_activate_fast(
    *,
    controller: str,
    priority_player: str,
    window: TimingWindow,
    is_chain_response: bool,
    spell_speed: SpellSpeed,
    chain_top_spell_speed: SpellSpeed | int | None,
) -> bool:
    if chain_top_spell_speed is not None:
        top_speed = (
            chain_top_spell_speed
            if isinstance(chain_top_spell_speed, SpellSpeed)
            else SpellSpeed(int(chain_top_spell_speed))
        )
        if (
            is_chain_response
            and top_speed == SpellSpeed.SS3
            and spell_speed != SpellSpeed.SS3
        ):
            return False

    resolver = FastEffectResolver()
    candidates = resolver.activatable_effects(
        effects=(
            FastEffect(
                effect_id="candidate",
                controller=controller,
                spell_speed=spell_speed,
            ),
        ),
        window=window,
        priority_player=priority_player,
        is_chain_response=is_chain_response,
    )
    return bool(candidates)


def _zone(
    state: MutableMapping[str, object],
    key: str,
    player: str,
) -> list[str]:
    zones_obj = state.setdefault(key, {})
    if not isinstance(zones_obj, dict):
        raise TypeError(f"state[{key!r}] must be a dict")
    zones = cast(dict[str, object], zones_obj)
    cards_obj = zones.setdefault(player, [])
    if not isinstance(cards_obj, list):
        raise TypeError(f"state[{key!r}][{player!r}] must be a list")
    cards = cast(list[str], cards_obj)
    return cards


def _player_scalar_map(
    state: MutableMapping[str, object],
    key: str,
) -> dict[str, object]:
    value = state.setdefault(key, {})
    if not isinstance(value, dict):
        raise TypeError(f"state[{key!r}] must be a dict")
    return cast(dict[str, object], value)


def _player_nested_map(
    state: MutableMapping[str, object],
    key: str,
    player: str,
) -> dict[str, object]:
    value = state.setdefault(key, {})
    if not isinstance(value, dict):
        raise TypeError(f"state[{key!r}] must be a dict")
    by_player = cast(dict[str, object], value)
    nested = by_player.setdefault(player, {})
    if not isinstance(nested, dict):
        raise TypeError(f"state[{key!r}][{player!r}] must be a dict")
    return cast(dict[str, object], nested)


def _draw(state: MutableMapping[str, object], *, controller: str, count: int) -> None:
    deck = _zone(state, "decks", controller)
    hand = _zone(state, "hands", controller)
    draw_count = min(count, len(deck))
    for _ in range(draw_count):
        hand.append(deck.pop(0))


def _as_dict(value: object) -> dict[str, object]:
    return cast(dict[str, object], value) if isinstance(value, dict) else {}


def _to_int(value: object, *, default: int) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    return default


__all__ = [
    "CHESHIRE_CAT_ID",
    "DORMOUSE_ID",
    "IN_UNDERGROUND_ID",
    "MARCH_HARE_ID",
    "MTP07_ID",
    "WHITE_RABBIT_ID",
    "cheshire_cat_main_phase_banish_self_draw_two",
    "dormouse_main_phase_exclude_from_deck_and_atk_boost",
    "in_underground_activation_optional_exclude",
    "march_hare_quick_exclude_and_ss_from_hand",
    "mtp07_trap_activation_search_monster",
    "p3_banish_trigger_pay_lp_and_ss",
    "white_rabbit_trigger_set_trap",
]
