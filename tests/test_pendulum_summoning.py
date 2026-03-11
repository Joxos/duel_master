import pytest

from duel_engine.actions import InvalidActionError
from duel_engine.models import Card, Zone
from duel_engine.summoning import (
    PendulumCard,
    PendulumZone,
    pendulum_summon,
)


def _pendulum(
    name: str, *, level: int, scale: int, source_zone: Zone = Zone.HAND
) -> PendulumCard:
    return PendulumCard(
        card=Card(name=name, card_type="MONSTER", owner_id="p1", face_up=False),
        level=level,
        pendulum_scale=scale,
        source_zone=source_zone,
    )


def _spell(name: str) -> Card:
    return Card(name=name, card_type="SPELL", owner_id="p1", face_up=False)


def test_pendulum_summon_from_hand_with_both_scales_on_field():
    scales = {
        PendulumZone.PZ_LEFT: _pendulum("Scale 1", level=4, scale=1),
        PendulumZone.PZ_RIGHT: _pendulum("Scale 8", level=4, scale=8),
    }
    monsters = (
        _pendulum("Odd-Eyes Pendulum Dragon", level=7, scale=4),
        _pendulum("Timegazer Magician", level=3, scale=8),
    )

    result = pendulum_summon(scales, monsters, (Zone.MZ_1, Zone.MZ_3))

    assert len(result) == 2
    assert result[0].zone is Zone.MZ_1
    assert result[1].zone is Zone.MZ_3
    assert all(entry.position == "FACE_UP_ATTACK" for entry in result)
    assert all(entry.card.face_up is True for entry in result)


def test_pendulum_summon_requires_both_scales_present():
    scales = {
        PendulumZone.PZ_LEFT: _pendulum("Scale 1", level=4, scale=1),
    }

    with pytest.raises(InvalidActionError, match="both pendulum scales"):
        _ = pendulum_summon(
            scales,
            (_pendulum("Target", level=4, scale=3),),
            (Zone.MZ_0,),
        )


def test_pendulum_card_scale_must_be_between_1_and_13():
    with pytest.raises(InvalidActionError, match="between 1 and 13"):
        _ = _pendulum("Invalid Scale", level=4, scale=0)

    with pytest.raises(InvalidActionError, match="between 1 and 13"):
        _ = _pendulum("Invalid Scale", level=4, scale=14)


def test_pendulum_summon_validates_level_between_scales():
    scales = {
        PendulumZone.PZ_LEFT: _pendulum("Scale 2", level=4, scale=2),
        PendulumZone.PZ_RIGHT: _pendulum("Scale 7", level=4, scale=7),
    }

    with pytest.raises(InvalidActionError, match="strictly between"):
        _ = pendulum_summon(
            scales, (_pendulum("Too Low", level=2, scale=3),), (Zone.MZ_2,)
        )

    with pytest.raises(InvalidActionError, match="strictly between"):
        _ = pendulum_summon(
            scales, (_pendulum("Too High", level=7, scale=3),), (Zone.MZ_2,)
        )


def test_pendulum_summon_from_hand_requires_main_monster_zone():
    scales = {
        PendulumZone.PZ_LEFT: _pendulum("Scale 1", level=4, scale=1),
        PendulumZone.PZ_RIGHT: _pendulum("Scale 8", level=4, scale=8),
    }

    with pytest.raises(InvalidActionError, match="main monster zone"):
        _ = pendulum_summon(
            scales, (_pendulum("Target", level=4, scale=4),), (Zone.EMZ_0,)
        )


def test_extra_deck_pendulum_monster_is_placed_face_up_in_extra_deck():
    scales = {
        PendulumZone.PZ_LEFT: _pendulum("Scale 1", level=4, scale=1),
        PendulumZone.PZ_RIGHT: _pendulum("Scale 8", level=4, scale=8),
    }
    monster = _pendulum(
        "Odd-Eyes Rebellion Dragon", level=7, scale=4, source_zone=Zone.EXTRA
    )

    result = pendulum_summon(scales, (monster,), (Zone.EXTRA,))

    assert len(result) == 1
    assert result[0].zone is Zone.EXTRA
    assert result[0].card.face_up is True


def test_extra_deck_pendulum_monster_rejects_non_extra_destination():
    scales = {
        PendulumZone.PZ_LEFT: _pendulum("Scale 1", level=4, scale=1),
        PendulumZone.PZ_RIGHT: _pendulum("Scale 8", level=4, scale=8),
    }
    monster = _pendulum(
        "Odd-Eyes Rebellion Dragon", level=7, scale=4, source_zone=Zone.EXTRA
    )

    with pytest.raises(InvalidActionError, match="face-up in Extra Deck"):
        _ = pendulum_summon(scales, (monster,), (Zone.MZ_0,))


def test_pendulum_card_must_be_monster():
    with pytest.raises(InvalidActionError, match="must be a monster"):
        _ = PendulumCard(card=_spell("Spell"), level=4, pendulum_scale=2)
