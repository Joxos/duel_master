import pytest

from duel_engine.actions import InvalidActionError
from duel_engine.models import Card, Zone
from duel_engine.summoning import (
    ExtraSummonType,
    fusion_summon,
    synchro_summon,
    xyz_summon,
)


def _monster(name: str) -> Card:
    return Card(name=name, card_type="MONSTER", owner_id="p1", face_up=False)


def _spell(name: str) -> Card:
    return Card(name=name, card_type="SPELL", owner_id="p1", face_up=False)


def test_fusion_summon_to_emz_sends_materials_to_gy():
    materials = (_monster("Poly Mat A"), _monster("Poly Mat B"))
    fusion = _monster("Flame Swordsman")

    result = fusion_summon(materials, fusion, Zone.EMZ_0)

    assert result.summon_type is ExtraSummonType.FUSION
    assert result.zone is Zone.EMZ_0
    assert result.position == "FACE_UP_ATTACK"
    assert result.card.face_up is True
    assert result.card.id == fusion.id
    assert result.sent_to_gy == materials
    assert result.overlay_materials == ()


def test_synchro_summon_to_main_monster_zone_is_legal_under_mr2020():
    tuner = _monster("Junk Synchron")
    non_tuners = (_monster("Speed Warrior"),)
    synchro = _monster("Junk Warrior")

    result = synchro_summon(tuner, non_tuners, synchro, Zone.MZ_2)

    assert result.summon_type is ExtraSummonType.SYNCHRO
    assert result.zone is Zone.MZ_2
    assert result.sent_to_gy == (tuner, *non_tuners)
    assert result.overlay_materials == ()


def test_xyz_summon_attaches_materials_as_overlay():
    materials = (_monster("Goblindbergh"), _monster("Kagetokage"))
    xyz = _monster("Number 39: Utopia")

    result = xyz_summon(materials, xyz, Zone.EMZ_1)

    assert result.summon_type is ExtraSummonType.XYZ
    assert result.zone is Zone.EMZ_1
    assert result.sent_to_gy == ()
    assert result.overlay_materials == materials


def test_extra_summon_rejects_occupied_zone_for_emz_or_mz():
    with pytest.raises(InvalidActionError, match="already occupied"):
        _ = fusion_summon(
            (_monster("A"),),
            _monster("Fusion"),
            Zone.EMZ_0,
            occupied_zones={Zone.EMZ_0},
        )

    with pytest.raises(InvalidActionError, match="already occupied"):
        _ = xyz_summon(
            (_monster("A"), _monster("B")),
            _monster("Xyz"),
            Zone.MZ_1,
            occupied_zones={Zone.MZ_1},
        )


def test_extra_summon_rejects_non_monster_result_card():
    with pytest.raises(InvalidActionError, match="monster cards"):
        _ = fusion_summon((_monster("A"),), _spell("Polymerization"), Zone.EMZ_0)


def test_synchro_requires_non_tuner_material():
    with pytest.raises(InvalidActionError, match="tuner and non-tuner"):
        _ = synchro_summon(
            _monster("Junk Synchron"), (), _monster("Junk Warrior"), Zone.MZ_0
        )


def test_xyz_requires_at_least_two_materials():
    with pytest.raises(InvalidActionError, match="at least 2"):
        _ = xyz_summon((_monster("Single"),), _monster("Xyz Monster"), Zone.MZ_0)


def test_materials_must_be_distinct():
    duplicated = _monster("Duplicate")

    with pytest.raises(InvalidActionError, match="distinct"):
        _ = fusion_summon((duplicated, duplicated), _monster("Fusion"), Zone.MZ_0)


def test_extra_summon_rejects_non_monster_zone():
    with pytest.raises(
        InvalidActionError, match="main monster zone or extra monster zone"
    ):
        _ = xyz_summon((_monster("A"), _monster("B")), _monster("Xyz"), Zone.SZ_0)
