from dataclasses import FrozenInstanceError

import pytest

from duel_engine.models import (
    EXTRA_MONSTER_ZONES,
    MAIN_MONSTER_ZONES,
    SCHEMA_VERSION,
    SPELL_TRAP_ZONES,
    Card,
    GameState,
    Player,
    Zone,
    omniscient_view,
    player_view,
)


def test_card_has_unique_id_and_opaque_reference():
    c1 = Card(
        name="Blue-Eyes White Dragon", card_type="MONSTER", owner_id="p1", face_up=False
    )
    c2 = Card(name="Dark Magician", card_type="MONSTER", owner_id="p1", face_up=False)

    assert c1.id != c2.id
    assert c1.opaque_ref != c2.opaque_ref
    assert c1.visible_identifier(reveal=False).startswith("hidden_")
    assert c1.visible_identifier(reveal=False) != c1.id


def test_models_are_immutableish():
    player = Player(id="p1")

    with pytest.raises(FrozenInstanceError):
        player.life_points = 7000


def test_zone_definitions_match_expected_slots():
    assert MAIN_MONSTER_ZONES == (Zone.MZ_0, Zone.MZ_1, Zone.MZ_2, Zone.MZ_3, Zone.MZ_4)
    assert SPELL_TRAP_ZONES == (Zone.SZ_0, Zone.SZ_1, Zone.SZ_2, Zone.SZ_3, Zone.SZ_4)
    assert EXTRA_MONSTER_ZONES == (Zone.EMZ_0, Zone.EMZ_1)
    assert Zone.FZ.value == "FZ"


def test_gamestate_json_roundtrip_with_schema_version():
    p1 = Player(
        id="p1",
        hand=(
            Card(name="Ash Blossom", card_type="MONSTER", owner_id="p1", face_up=True),
        ),
        deck=(
            Card(
                name="Mystical Space Typhoon",
                card_type="SPELL",
                owner_id="p1",
                face_up=False,
            ),
        ),
    )
    p2 = Player(id="p2")
    state = GameState(
        players=(p1, p2), turn=3, phase="MAIN1", step="OPEN", priority_player="p1"
    )

    payload = state.to_json()
    restored = GameState.from_json(payload)

    assert restored == state
    assert restored.to_dict()["schema_version"] == SCHEMA_VERSION


def test_player_view_hides_opponent_private_information():
    p1_hand = Card(name='Maxx "C"', card_type="MONSTER", owner_id="p1", face_up=False)
    p2_hand = Card(name="Nibiru", card_type="MONSTER", owner_id="p2", face_up=False)
    p2_gy = Card(name="Raigeki", card_type="SPELL", owner_id="p2", face_up=True)
    p2_banished_fd = Card(
        name="Secret Card", card_type="TRAP", owner_id="p2", face_up=False
    )

    state = GameState(
        players=(
            Player(id="p1", hand=(p1_hand,)),
            Player(
                id="p2", hand=(p2_hand,), graveyard=(p2_gy,), banished=(p2_banished_fd,)
            ),
        ),
        priority_player="p1",
    )

    view = player_view(state, "p1")
    my_hand = view["players"][0]["hand"][0]
    opp_hand = view["players"][1]["hand"][0]
    opp_gy = view["players"][1]["graveyard"][0]
    opp_banished_fd = view["players"][1]["banished"][0]

    assert my_hand["id"] == p1_hand.id
    assert my_hand["name"] == 'Maxx "C"'

    assert opp_hand["id"] == p2_hand.opaque_ref
    assert opp_hand["name"] is None
    assert opp_hand["card_type"] is None

    assert opp_gy["id"] == p2_gy.id
    assert opp_gy["name"] == "Raigeki"
    assert opp_banished_fd["id"] == p2_banished_fd.opaque_ref
    assert opp_banished_fd["name"] is None


def test_omniscient_view_matches_state_dict():
    state = GameState(players=(Player(id="p1"), Player(id="p2")))
    assert omniscient_view(state) == state.to_dict()
