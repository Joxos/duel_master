from __future__ import annotations

from enum import Enum


class TurnPhase(str, Enum):
    DRAW = "DRAW"
    STANDBY = "STANDBY"
    MAIN1 = "MAIN1"
    BATTLE = "BATTLE"
    MAIN2 = "MAIN2"
    END = "END"


class TurnStep(str, Enum):
    BATTLE_START = "BATTLE_START"
    DAMAGE_STEP = "DAMAGE_STEP"
    DAMAGE_END = "DAMAGE_END"
