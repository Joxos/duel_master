from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class ZoneType(Enum):
    NONE = "无"
    HAND = "手牌"
    MAIN_MONSTER_ZONE_1 = "主要怪兽区1"
    MAIN_MONSTER_ZONE_2 = "主要怪兽区2"
    MAIN_MONSTER_ZONE_3 = "主要怪兽区3"
    MAIN_MONSTER_ZONE_4 = "主要怪兽区4"
    MAIN_MONSTER_ZONE_5 = "主要怪兽区5"
    MAIN_MONSTER_ZONE = [
        MAIN_MONSTER_ZONE_1,
        MAIN_MONSTER_ZONE_2,
        MAIN_MONSTER_ZONE_3,
        MAIN_MONSTER_ZONE_4,
        MAIN_MONSTER_ZONE_5,
    ]
    EXTRA_MONSTER_ZONE_1 = "额外怪兽区1"
    EXTRA_MONSTER_ZONE_2 = "额外怪兽区2"
    EXTRA_MONSTER_ZONE = [EXTRA_MONSTER_ZONE_1, EXTRA_MONSTER_ZONE_2]
    SPELL_TRAP_ZONE_1 = "魔陷区1"
    SPELL_TRAP_ZONE_2 = "魔陷区2"
    SPELL_TRAP_ZONE_3 = "魔陷区3"
    SPELL_TRAP_ZONE_4 = "魔陷区4"
    SPELL_TRAP_ZONE_5 = "魔陷区5"
    SPELL_TRAP_ZONE = [
        SPELL_TRAP_ZONE_1,
        SPELL_TRAP_ZONE_2,
        SPELL_TRAP_ZONE_3,
        SPELL_TRAP_ZONE_4,
        SPELL_TRAP_ZONE_5,
    ]
    FIELD_ZONE = "场地区"
    GRAVEYARD = "墓地"
    BANISHED = "除外区"
    MAIN_DECK = "卡组"
    EXTRA_DECK = "额外卡组"
    OVERLAY = "超量素材"
