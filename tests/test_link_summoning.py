import pytest

from duel_engine.actions import InvalidActionError
from duel_engine.models import Zone
from duel_engine.summoning import (
    LinkMarker,
    LinkMonster,
    LinkSummonType,
    link_summon,
    pointed_main_monster_zones,
)


def _monster(name: str):
    from duel_engine.models import Card

    return Card(name=name, card_type="MONSTER", owner_id="p1", face_up=False)


def _link_monster(name: str, rating: int, markers: set[LinkMarker]) -> LinkMonster:
    return LinkMonster(
        card=_monster(name),
        link_rating=rating,
        link_markers=frozenset(markers),
    )


def test_link_summon_to_emz_is_legal():
    link2 = _link_monster(
        "Link Spider Duo", 2, {LinkMarker.BOTTOM_LEFT, LinkMarker.BOTTOM_RIGHT}
    )
    materials = (_monster("Mat A"), _monster("Mat B"))

    result = link_summon(materials, link2, Zone.EMZ_0)

    assert result.summon_type is LinkSummonType.LINK
    assert result.zone is Zone.EMZ_0
    assert result.position == "FACE_UP_ATTACK"
    assert result.card.face_up is True
    assert result.sent_to_gy == materials


def test_link_markers_from_emz_point_to_main_monster_zones():
    emz_link = link_summon(
        (_monster("Mat A"), _monster("Mat B")),
        _link_monster(
            "Knightmare Phoenix", 2, {LinkMarker.BOTTOM_LEFT, LinkMarker.BOTTOM_RIGHT}
        ),
        Zone.EMZ_0,
    )

    pointed = pointed_main_monster_zones((emz_link,))
    assert pointed == frozenset({Zone.MZ_0, Zone.MZ_2})


def test_link_summon_to_mz_requires_existing_marker_pointing():
    emz_link = link_summon(
        (_monster("Mat A"), _monster("Mat B")),
        _link_monster(
            "Proxy Dragon", 2, {LinkMarker.BOTTOM_LEFT, LinkMarker.BOTTOM_RIGHT}
        ),
        Zone.EMZ_0,
    )

    new_link = _link_monster(
        "Decode Talker", 3, {LinkMarker.BOTTOM, LinkMarker.LEFT, LinkMarker.RIGHT}
    )
    materials = (_monster("Mat C"), _monster("Mat D"), _monster("Mat E"))

    result = link_summon(
        materials,
        new_link,
        Zone.MZ_2,
        occupied_zones={Zone.EMZ_0},
        link_monsters=(emz_link,),
    )
    assert result.zone is Zone.MZ_2

    with pytest.raises(InvalidActionError, match="link marker"):
        _ = link_summon(
            materials,
            new_link,
            Zone.MZ_4,
            occupied_zones={Zone.EMZ_0},
            link_monsters=(emz_link,),
        )


def test_link_summon_rejects_occupied_emz_or_mz():
    link2 = _link_monster(
        "Link-2", 2, {LinkMarker.BOTTOM_LEFT, LinkMarker.BOTTOM_RIGHT}
    )
    materials = (_monster("Mat A"), _monster("Mat B"))

    with pytest.raises(InvalidActionError, match="already occupied"):
        _ = link_summon(materials, link2, Zone.EMZ_1, occupied_zones={Zone.EMZ_1})

    emz_link = link_summon(materials, link2, Zone.EMZ_0)
    with pytest.raises(InvalidActionError, match="already occupied"):
        _ = link_summon(
            materials,
            link2,
            Zone.MZ_0,
            occupied_zones={Zone.EMZ_0, Zone.MZ_0},
            link_monsters=(emz_link,),
        )


def test_link_summon_requires_material_count_matching_rating():
    link3 = _link_monster(
        "Tri-Link", 3, {LinkMarker.BOTTOM, LinkMarker.LEFT, LinkMarker.RIGHT}
    )

    with pytest.raises(InvalidActionError, match="matching the monster's link rating"):
        _ = link_summon((_monster("A"), _monster("B")), link3, Zone.EMZ_0)


def test_link_monster_markers_must_match_rating():
    invalid = _link_monster("Broken Link", 3, {LinkMarker.BOTTOM, LinkMarker.LEFT})
    with pytest.raises(InvalidActionError, match="markers must match"):
        _ = link_summon(
            (_monster("A"), _monster("B"), _monster("C")),
            invalid,
            Zone.EMZ_0,
        )
