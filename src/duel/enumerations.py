from enum import Enum


class END_REASON(Enum):
    LIFE_POINTS = "生命值归零"
    DECK_OUT = "卡组耗尽"
    SURRENDER = "认输"
    TIME_OUT = "时间到"
