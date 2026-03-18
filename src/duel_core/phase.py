from enum import StrEnum


class Phase(StrEnum):
    DRAW = "Draw"
    STANDBY = "Standby"
    MAIN_1 = "Main Phase 1"
    BATTLE = "Battle"
    MAIN_2 = "Main Phase 2"
    END = "End"
