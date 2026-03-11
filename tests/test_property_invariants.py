from __future__ import annotations

from hypothesis import given, strategies as st
import pytest

from duel_engine.actions import InvalidActionError
from duel_engine.models import (
    Card,
    GameState,
    MAIN_MONSTER_ZONES,
    Player,
    Zone,
    player_view,
)
from duel_engine.rng import deterministic_shuffle_hash
from duel_engine.summoning import flip_summon, normal_summon


def _cards(
    owner_id: str, count: int, *, face_up: bool, prefix: str
) -> tuple[Card, ...]:
    return tuple(
        Card(
            id=f"{prefix}_{owner_id}_{idx}",
            opaque_ref=f"hidden_{prefix}_{owner_id}_{idx}",
            name=f"{prefix}_name_{idx}",
            card_type="MONSTER",
            owner_id=owner_id,
            face_up=face_up,
        )
        for idx in range(count)
    )


def _field_count(_state: GameState) -> int:
    return 0


@given(
    p1_deck=st.integers(min_value=0, max_value=40),
    p1_hand=st.integers(min_value=0, max_value=10),
    p1_gy=st.integers(min_value=0, max_value=20),
    p1_banished=st.integers(min_value=0, max_value=20),
    p2_deck=st.integers(min_value=0, max_value=40),
    p2_hand=st.integers(min_value=0, max_value=10),
    p2_gy=st.integers(min_value=0, max_value=20),
    p2_banished=st.integers(min_value=0, max_value=20),
)
def test_property_card_count_conservation(
    p1_deck: int,
    p1_hand: int,
    p1_gy: int,
    p1_banished: int,
    p2_deck: int,
    p2_hand: int,
    p2_gy: int,
    p2_banished: int,
) -> None:
    p1 = Player(
        id="p1",
        deck=_cards("p1", p1_deck, face_up=False, prefix="d"),
        hand=_cards("p1", p1_hand, face_up=False, prefix="h"),
        graveyard=_cards("p1", p1_gy, face_up=True, prefix="g"),
        banished=_cards("p1", p1_banished, face_up=True, prefix="b"),
    )
    p2 = Player(
        id="p2",
        deck=_cards("p2", p2_deck, face_up=False, prefix="d"),
        hand=_cards("p2", p2_hand, face_up=False, prefix="h"),
        graveyard=_cards("p2", p2_gy, face_up=True, prefix="g"),
        banished=_cards("p2", p2_banished, face_up=True, prefix="b"),
    )
    state = GameState(players=(p1, p2))

    expected_total = (
        p1_deck
        + p1_hand
        + p1_gy
        + p1_banished
        + p2_deck
        + p2_hand
        + p2_gy
        + p2_banished
    )
    observed_total = sum(
        len(player.deck)
        + len(player.hand)
        + _field_count(state)
        + len(player.graveyard)
        + len(player.banished)
        for player in state.players
    )

    assert observed_total == expected_total


@given(
    my_hand_size=st.integers(min_value=1, max_value=7),
    opp_hand_size=st.integers(min_value=1, max_value=7),
)
def test_property_hidden_info_not_leaked(my_hand_size: int, opp_hand_size: int) -> None:
    p1 = Player(
        id="p1", hand=_cards("p1", my_hand_size, face_up=False, prefix="self_hand")
    )
    p2_hidden_hand = _cards("p2", opp_hand_size, face_up=False, prefix="opp_hand")
    p2 = Player(id="p2", hand=p2_hidden_hand)
    state = GameState(players=(p1, p2), priority_player="p1")

    view = player_view(state, "p1")
    players_view = view["players"]
    assert isinstance(players_view, list)
    opp_player_view = players_view[1]
    assert isinstance(opp_player_view, dict)
    opp_hand_view = opp_player_view["hand"]
    assert isinstance(opp_hand_view, list)

    assert len(opp_hand_view) == opp_hand_size
    for projected in opp_hand_view:
        assert isinstance(projected, dict)
        assert isinstance(projected["id"], str)
        assert projected["id"].startswith("hidden_")
        assert projected["name"] is None
        assert projected["card_type"] is None


@given(
    invalid_zone=st.sampled_from(
        [zone for zone in Zone if zone not in MAIN_MONSTER_ZONES]
    ),
)
def test_property_illegal_actions_rejected(invalid_zone: Zone) -> None:
    with pytest.raises(InvalidActionError):
        _ = normal_summon(
            Card(
                name="Property Monster",
                card_type="MONSTER",
                owner_id="p1",
                face_up=False,
            ),
            invalid_zone,
        )

    with pytest.raises(InvalidActionError):
        _ = flip_summon(
            Card(
                name="Face-up Monster", card_type="MONSTER", owner_id="p1", face_up=True
            )
        )


@given(
    seed=st.integers(min_value=0, max_value=2**32 - 1),
    values=st.lists(st.text(min_size=0, max_size=12), min_size=1, max_size=50),
)
def test_property_determinism_invariant(seed: int, values: list[str]) -> None:
    first = deterministic_shuffle_hash(seed=seed, values=values)
    second = deterministic_shuffle_hash(seed=seed, values=values)
    assert first == second
