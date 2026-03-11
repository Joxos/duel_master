from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from duel_engine.actions.errors import InvalidActionError
from duel_engine.models import EXTRA_MONSTER_ZONES, MAIN_MONSTER_ZONES, Card, Zone

from .types import ExtraSummonType


@dataclass(frozen=True, slots=True)
class ExtraSummonedMonster:
    card: Card
    zone: Zone
    summon_type: ExtraSummonType
    position: str
    sent_to_gy: tuple[Card, ...]
    overlay_materials: tuple[Card, ...]


def _validate_extra_summon_zone(zone: Zone, occupied_zones: set[Zone] | None) -> None:
    if zone not in MAIN_MONSTER_ZONES and zone not in EXTRA_MONSTER_ZONES:
        raise InvalidActionError(
            "Extra deck summon must use a main monster zone or extra monster zone"
        )

    if occupied_zones is not None and zone in occupied_zones:
        raise InvalidActionError(f"Zone {zone.value} is already occupied")


def _validate_monster_card(card: Card) -> None:
    if card.card_type != "MONSTER":
        raise InvalidActionError("Only monster cards can be summoned")


def _ensure_unique_materials(materials: Sequence[Card]) -> tuple[Card, ...]:
    ids = [card.id for card in materials]
    if len(set(ids)) != len(ids):
        raise InvalidActionError("Summon materials must be distinct cards")
    return tuple(materials)


def fusion_summon(
    materials: Sequence[Card],
    monster_card: Card,
    zone: Zone,
    *,
    occupied_zones: set[Zone] | None = None,
) -> ExtraSummonedMonster:
    if not materials:
        raise InvalidActionError("Fusion summon requires at least 1 material")

    _validate_monster_card(monster_card)
    _validate_extra_summon_zone(zone, occupied_zones)
    material_cards = _ensure_unique_materials(materials)

    return ExtraSummonedMonster(
        card=Card(
            id=monster_card.id,
            name=monster_card.name,
            card_type=monster_card.card_type,
            owner_id=monster_card.owner_id,
            face_up=True,
            opaque_ref=monster_card.opaque_ref,
        ),
        zone=zone,
        summon_type=ExtraSummonType.FUSION,
        position="FACE_UP_ATTACK",
        sent_to_gy=material_cards,
        overlay_materials=(),
    )


def synchro_summon(
    tuner: Card,
    non_tuners: Sequence[Card],
    monster_card: Card,
    zone: Zone,
    *,
    occupied_zones: set[Zone] | None = None,
) -> ExtraSummonedMonster:
    if not non_tuners:
        raise InvalidActionError(
            "Synchro summon requires a tuner and non-tuner materials"
        )

    _validate_monster_card(monster_card)
    _validate_monster_card(tuner)
    for non_tuner in non_tuners:
        _validate_monster_card(non_tuner)

    _validate_extra_summon_zone(zone, occupied_zones)
    material_cards = _ensure_unique_materials((tuner, *non_tuners))

    return ExtraSummonedMonster(
        card=Card(
            id=monster_card.id,
            name=monster_card.name,
            card_type=monster_card.card_type,
            owner_id=monster_card.owner_id,
            face_up=True,
            opaque_ref=monster_card.opaque_ref,
        ),
        zone=zone,
        summon_type=ExtraSummonType.SYNCHRO,
        position="FACE_UP_ATTACK",
        sent_to_gy=material_cards,
        overlay_materials=(),
    )


def xyz_summon(
    materials: Sequence[Card],
    monster_card: Card,
    zone: Zone,
    *,
    occupied_zones: set[Zone] | None = None,
) -> ExtraSummonedMonster:
    if len(materials) < 2:
        raise InvalidActionError("Xyz summon requires at least 2 materials")

    _validate_monster_card(monster_card)
    _validate_extra_summon_zone(zone, occupied_zones)
    material_cards = _ensure_unique_materials(materials)

    return ExtraSummonedMonster(
        card=Card(
            id=monster_card.id,
            name=monster_card.name,
            card_type=monster_card.card_type,
            owner_id=monster_card.owner_id,
            face_up=True,
            opaque_ref=monster_card.opaque_ref,
        ),
        zone=zone,
        summon_type=ExtraSummonType.XYZ,
        position="FACE_UP_ATTACK",
        sent_to_gy=(),
        overlay_materials=material_cards,
    )
