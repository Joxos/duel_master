from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum

from duel_engine.actions.errors import InvalidActionError
from duel_engine.models import MAIN_MONSTER_ZONES, Card, Zone


class PendulumZone(str, Enum):
    PZ_LEFT = "PZ_LEFT"
    PZ_RIGHT = "PZ_RIGHT"


@dataclass(frozen=True, slots=True)
class PendulumCard:
    card: Card
    level: int
    pendulum_scale: int
    source_zone: Zone = Zone.HAND

    def __post_init__(self) -> None:
        if self.card.card_type != "MONSTER":
            raise InvalidActionError("Pendulum card must be a monster card")

        if self.level <= 0:
            raise InvalidActionError("Pendulum monster level must be positive")

        if not 1 <= self.pendulum_scale <= 13:
            raise InvalidActionError("Pendulum scale must be between 1 and 13")


@dataclass(frozen=True, slots=True)
class PendulumSummonedMonster:
    card: Card
    zone: Zone
    position: str


def pendulum_summon(
    pendulum_cards: Mapping[PendulumZone, PendulumCard],
    monster_cards: Sequence[PendulumCard],
    zones: Sequence[Zone],
) -> tuple[PendulumSummonedMonster, ...]:
    if (
        PendulumZone.PZ_LEFT not in pendulum_cards
        or PendulumZone.PZ_RIGHT not in pendulum_cards
    ):
        raise InvalidActionError(
            "Pendulum summon requires both pendulum scales on the field"
        )

    left_scale = pendulum_cards[PendulumZone.PZ_LEFT].pendulum_scale
    right_scale = pendulum_cards[PendulumZone.PZ_RIGHT].pendulum_scale
    lower_scale = min(left_scale, right_scale)
    upper_scale = max(left_scale, right_scale)

    if lower_scale == upper_scale:
        raise InvalidActionError("Pendulum scales must be different")

    if len(monster_cards) != len(zones):
        raise InvalidActionError(
            "Pendulum summon monsters and zones must have the same count"
        )

    if len(set(zone.value for zone in zones)) != len(zones):
        raise InvalidActionError("Pendulum summon zones must be distinct")

    summoned: list[PendulumSummonedMonster] = []
    for monster_card, zone in zip(monster_cards, zones, strict=True):
        if not lower_scale < monster_card.level < upper_scale:
            raise InvalidActionError(
                "Pendulum monster level must be strictly between scales"
            )

        if monster_card.source_zone == Zone.HAND:
            if zone not in MAIN_MONSTER_ZONES:
                raise InvalidActionError(
                    "Pendulum summon from hand must use a main monster zone"
                )
        elif monster_card.source_zone == Zone.EXTRA:
            if zone is not Zone.EXTRA:
                raise InvalidActionError(
                    "Pendulum summon from extra deck must be placed face-up in Extra Deck"
                )
        else:
            raise InvalidActionError(
                "Pendulum summon supports only hand or extra deck pendulum monsters"
            )

        summoned.append(
            PendulumSummonedMonster(
                card=Card(
                    id=monster_card.card.id,
                    name=monster_card.card.name,
                    card_type=monster_card.card.card_type,
                    owner_id=monster_card.card.owner_id,
                    face_up=True,
                    opaque_ref=monster_card.card.opaque_ref,
                ),
                zone=zone,
                position="FACE_UP_ATTACK",
            )
        )

    return tuple(summoned)
