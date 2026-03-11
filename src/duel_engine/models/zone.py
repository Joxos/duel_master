from __future__ import annotations

from enum import Enum


class Zone(str, Enum):
    DECK = "DECK"
    HAND = "HAND"
    GY = "GY"
    BANISHED = "BANISHED"
    EXTRA = "EXTRA"

    MZ_0 = "MZ_0"
    MZ_1 = "MZ_1"
    MZ_2 = "MZ_2"
    MZ_3 = "MZ_3"
    MZ_4 = "MZ_4"

    SZ_0 = "SZ_0"
    SZ_1 = "SZ_1"
    SZ_2 = "SZ_2"
    SZ_3 = "SZ_3"
    SZ_4 = "SZ_4"

    FZ = "FZ"

    EMZ_0 = "EMZ_0"
    EMZ_1 = "EMZ_1"


MAIN_MONSTER_ZONES: tuple[Zone, ...] = (
    Zone.MZ_0,
    Zone.MZ_1,
    Zone.MZ_2,
    Zone.MZ_3,
    Zone.MZ_4,
)

SPELL_TRAP_ZONES: tuple[Zone, ...] = (
    Zone.SZ_0,
    Zone.SZ_1,
    Zone.SZ_2,
    Zone.SZ_3,
    Zone.SZ_4,
)

EXTRA_MONSTER_ZONES: tuple[Zone, ...] = (Zone.EMZ_0, Zone.EMZ_1)
