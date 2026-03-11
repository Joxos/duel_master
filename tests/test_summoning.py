import pytest

from duel_engine.actions import InvalidActionError
from duel_engine.models import Card, Zone
from duel_engine.summoning import (
    SummonTracker,
    SummonType,
    flip_summon,
    normal_summon,
    set_monster,
)


def _monster(face_up: bool = True) -> Card:
    return Card(
        name="Gene-Warped Warwolf", card_type="MONSTER", owner_id="p1", face_up=face_up
    )


def test_normal_summon_places_face_up_attack_and_marks_type():
    card = _monster(face_up=False)

    result = normal_summon(card, Zone.MZ_2)

    assert result.summon_type is SummonType.NORMAL
    assert result.zone is Zone.MZ_2
    assert result.position == "FACE_UP_ATTACK"
    assert result.card.face_up is True
    assert result.card.id == card.id


def test_set_monster_places_face_down_defense_and_marks_type():
    card = _monster(face_up=True)

    result = set_monster(card, Zone.MZ_3)

    assert result.summon_type is SummonType.SET
    assert result.zone is Zone.MZ_3
    assert result.position == "FACE_DOWN_DEFENSE"
    assert result.card.face_up is False
    assert result.card.id == card.id


def test_flip_summon_flips_face_down_monster_to_face_up_attack():
    card = _monster(face_up=False)

    result = flip_summon(card)

    assert result.summon_type is SummonType.FLIP
    assert result.position == "FACE_UP_ATTACK"
    assert result.card.face_up is True
    assert result.zone is None


def test_flip_summon_rejects_face_up_monster():
    with pytest.raises(InvalidActionError, match="face-down"):
        _ = flip_summon(_monster(face_up=True))


def test_normal_summon_rejects_non_main_monster_zone():
    with pytest.raises(InvalidActionError, match="main monster zone"):
        _ = normal_summon(_monster(), Zone.SZ_0)


def test_set_monster_rejects_occupied_zone():
    with pytest.raises(InvalidActionError, match="already occupied"):
        _ = set_monster(_monster(), Zone.MZ_1, occupied_zones={Zone.MZ_1})


def test_normal_summon_once_per_turn_limit_blocks_second_normal_summon():
    tracker = SummonTracker()

    _ = normal_summon(_monster(), Zone.MZ_0, summon_tracker=tracker)

    with pytest.raises(InvalidActionError, match="already been used"):
        _ = normal_summon(_monster(), Zone.MZ_4, summon_tracker=tracker)


def test_set_consumes_normal_summon_limit_too():
    tracker = SummonTracker()

    _ = set_monster(_monster(), Zone.MZ_0, summon_tracker=tracker)

    with pytest.raises(InvalidActionError, match="already been used"):
        _ = normal_summon(_monster(), Zone.MZ_1, summon_tracker=tracker)


def test_reset_turn_restores_normal_summon_availability():
    tracker = SummonTracker()
    _ = normal_summon(_monster(), Zone.MZ_0, summon_tracker=tracker)

    tracker.reset_turn()

    result = set_monster(_monster(), Zone.MZ_1, summon_tracker=tracker)
    assert result.summon_type is SummonType.SET
