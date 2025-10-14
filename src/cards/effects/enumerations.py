from enum import Enum


class CHECK_TYPE(Enum):
    CARD = "卡片"
    NAME = "卡名"


class UNIT(Enum):
    TURN = "回合"
    DUEL = "决斗"
