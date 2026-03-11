from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from duel_engine.actions.errors import InvalidActionError
from duel_engine.models import MAIN_MONSTER_ZONES, Card, Zone

from .types import SummonType


@dataclass(frozen=True, slots=True)
class SummonedMonster:
    card: Card
    zone: Zone | None
    summon_type: SummonType
    position: str


class SummonTracker:
    __slots__: ClassVar[tuple[str, ...]] = ("_normal_summon_used",)

    def __init__(self) -> None:
        self._normal_summon_used: bool = False

    @property
    def normal_summon_used(self) -> bool:
        return self._normal_summon_used

    def consume_normal_summon(self) -> None:
        if self._normal_summon_used:
            raise InvalidActionError(
                "Normal summon/set has already been used this turn"
            )
        self._normal_summon_used = True

    def reset_turn(self) -> None:
        self._normal_summon_used = False


def _validate_monster_zone_available(
    zone: Zone, occupied_zones: set[Zone] | None
) -> None:
    if zone not in MAIN_MONSTER_ZONES:
        raise InvalidActionError("Normal summon/set must use a main monster zone")

    if occupied_zones is not None and zone in occupied_zones:
        raise InvalidActionError(f"Zone {zone.value} is already occupied")


def normal_summon(
    card: Card,
    zone: Zone,
    *,
    occupied_zones: set[Zone] | None = None,
    summon_tracker: SummonTracker | None = None,
) -> SummonedMonster:
    _validate_monster_zone_available(zone, occupied_zones)

    if summon_tracker is not None:
        summon_tracker.consume_normal_summon()

    return SummonedMonster(
        card=Card(
            id=card.id,
            name=card.name,
            card_type=card.card_type,
            owner_id=card.owner_id,
            face_up=True,
            opaque_ref=card.opaque_ref,
        ),
        zone=zone,
        summon_type=SummonType.NORMAL,
        position="FACE_UP_ATTACK",
    )


def set_monster(
    card: Card,
    zone: Zone,
    *,
    occupied_zones: set[Zone] | None = None,
    summon_tracker: SummonTracker | None = None,
) -> SummonedMonster:
    _validate_monster_zone_available(zone, occupied_zones)

    if summon_tracker is not None:
        summon_tracker.consume_normal_summon()

    return SummonedMonster(
        card=Card(
            id=card.id,
            name=card.name,
            card_type=card.card_type,
            owner_id=card.owner_id,
            face_up=False,
            opaque_ref=card.opaque_ref,
        ),
        zone=zone,
        summon_type=SummonType.SET,
        position="FACE_DOWN_DEFENSE",
    )


def flip_summon(card: Card) -> SummonedMonster:
    if card.face_up:
        raise InvalidActionError("Only a face-down monster can be flip summoned")

    return SummonedMonster(
        card=Card(
            id=card.id,
            name=card.name,
            card_type=card.card_type,
            owner_id=card.owner_id,
            face_up=True,
            opaque_ref=card.opaque_ref,
        ),
        zone=None,
        summon_type=SummonType.FLIP,
        position="FACE_UP_ATTACK",
    )
