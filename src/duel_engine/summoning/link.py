from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum

from duel_engine.actions.errors import InvalidActionError
from duel_engine.models import EXTRA_MONSTER_ZONES, MAIN_MONSTER_ZONES, Card, Zone

from .types import LinkSummonType


class LinkMarker(str, Enum):
    TOP_LEFT = "TOP_LEFT"
    TOP = "TOP"
    TOP_RIGHT = "TOP_RIGHT"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    BOTTOM_LEFT = "BOTTOM_LEFT"
    BOTTOM = "BOTTOM"
    BOTTOM_RIGHT = "BOTTOM_RIGHT"


@dataclass(frozen=True, slots=True)
class LinkMonster:
    card: Card
    link_rating: int
    link_markers: frozenset[LinkMarker]


@dataclass(frozen=True, slots=True)
class LinkSummonedMonster:
    card: Card
    zone: Zone
    summon_type: LinkSummonType
    position: str
    sent_to_gy: tuple[Card, ...]
    link_rating: int
    link_markers: frozenset[LinkMarker]


_ZONE_COORDS: dict[Zone, tuple[int, int]] = {
    Zone.MZ_0: (0, 0),
    Zone.MZ_1: (1, 0),
    Zone.MZ_2: (2, 0),
    Zone.MZ_3: (3, 0),
    Zone.MZ_4: (4, 0),
    Zone.EMZ_0: (1, 1),
    Zone.EMZ_1: (3, 1),
}

_COORD_TO_ZONE: dict[tuple[int, int], Zone] = {v: k for k, v in _ZONE_COORDS.items()}

_MARKER_DELTAS: dict[LinkMarker, tuple[int, int]] = {
    LinkMarker.TOP_LEFT: (-1, 1),
    LinkMarker.TOP: (0, 1),
    LinkMarker.TOP_RIGHT: (1, 1),
    LinkMarker.LEFT: (-1, 0),
    LinkMarker.RIGHT: (1, 0),
    LinkMarker.BOTTOM_LEFT: (-1, -1),
    LinkMarker.BOTTOM: (0, -1),
    LinkMarker.BOTTOM_RIGHT: (1, -1),
}


def _validate_monster_card(card: Card) -> None:
    if card.card_type != "MONSTER":
        raise InvalidActionError("Only monster cards can be summoned")


def _ensure_unique_materials(materials: Sequence[Card]) -> tuple[Card, ...]:
    ids = [card.id for card in materials]
    if len(set(ids)) != len(ids):
        raise InvalidActionError("Summon materials must be distinct cards")
    return tuple(materials)


def _pointed_zone(source_zone: Zone, marker: LinkMarker) -> Zone | None:
    source_coord = _ZONE_COORDS.get(source_zone)
    if source_coord is None:
        return None
    dx, dy = _MARKER_DELTAS[marker]
    target_coord = (source_coord[0] + dx, source_coord[1] + dy)
    return _COORD_TO_ZONE.get(target_coord)


def pointed_main_monster_zones(
    link_monsters: Sequence[LinkSummonedMonster],
) -> frozenset[Zone]:
    zones: set[Zone] = set()
    for link_monster in link_monsters:
        for marker in link_monster.link_markers:
            pointed = _pointed_zone(link_monster.zone, marker)
            if pointed is not None and pointed in MAIN_MONSTER_ZONES:
                zones.add(pointed)
    return frozenset(zones)


def _validate_link_zone(
    zone: Zone,
    *,
    occupied_zones: set[Zone] | None,
    link_monsters: Sequence[LinkSummonedMonster],
) -> None:
    if zone not in MAIN_MONSTER_ZONES and zone not in EXTRA_MONSTER_ZONES:
        raise InvalidActionError(
            "Link summon must use a main monster zone or extra monster zone"
        )

    if occupied_zones is not None and zone in occupied_zones:
        raise InvalidActionError(f"Zone {zone.value} is already occupied")

    if zone in EXTRA_MONSTER_ZONES:
        return

    pointed = pointed_main_monster_zones(link_monsters)
    if zone not in pointed:
        raise InvalidActionError(
            "Link summon to a main monster zone requires a link marker pointing to that zone"
        )


def link_summon(
    materials: Sequence[Card],
    monster_card: LinkMonster,
    zone: Zone,
    *,
    occupied_zones: set[Zone] | None = None,
    link_monsters: Sequence[LinkSummonedMonster] = (),
) -> LinkSummonedMonster:
    if monster_card.link_rating <= 0:
        raise InvalidActionError("Link monster must have positive link rating")

    if len(monster_card.link_markers) != monster_card.link_rating:
        raise InvalidActionError("Link monster markers must match link rating")

    material_cards = _ensure_unique_materials(materials)
    if len(material_cards) != monster_card.link_rating:
        raise InvalidActionError(
            "Link summon requires materials matching the monster's link rating"
        )

    _validate_monster_card(monster_card.card)
    for material in material_cards:
        _validate_monster_card(material)

    _validate_link_zone(
        zone,
        occupied_zones=occupied_zones,
        link_monsters=link_monsters,
    )

    return LinkSummonedMonster(
        card=Card(
            id=monster_card.card.id,
            name=monster_card.card.name,
            card_type=monster_card.card.card_type,
            owner_id=monster_card.card.owner_id,
            face_up=True,
            opaque_ref=monster_card.card.opaque_ref,
        ),
        zone=zone,
        summon_type=LinkSummonType.LINK,
        position="FACE_UP_ATTACK",
        sent_to_gy=material_cards,
        link_rating=monster_card.link_rating,
        link_markers=frozenset(monster_card.link_markers),
    )
