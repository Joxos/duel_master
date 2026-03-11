from __future__ import annotations

from enum import Enum


class TimingWindow(str, Enum):
    OPEN = "OPEN"
    DRAW = "DRAW"
    STANDBY = "STANDBY"
    MAIN1_OPEN = "MAIN1_OPEN"
    BATTLE_START = "BATTLE_START"
    DAMAGE = "DAMAGE"
    BATTLE_END = "BATTLE_END"
    MAIN2_OPEN = "MAIN2_OPEN"
    END_OPEN = "END_OPEN"


class SpellSpeed(int, Enum):
    SS1 = 1
    SS2 = 2
    SS3 = 3
