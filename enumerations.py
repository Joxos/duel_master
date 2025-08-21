from dataclasses import dataclass


class CARD:
    class MONSTER:
        NORMAL = "通常"
        EFFECT = "效果"
        RITUAL = "仪式"
        FUSION = "融合"
        SYNCHRO = "同调"
        XYZ = "超量"
        PENDULUM = "灵摆"
        LINK = "连接"

    class SPELL:
        NORMAL = "通常"
        FIELD = "场地"
        EQUIP = "装备"
        CONTINUOUS = "永续"
        QUICK_PLAY = "速攻"
        RITUAL = "仪式"

    class TRAP:
        NORMAL = "通常"
        CONTINUOUS = "永续"
        COUNTER = 1


class SPECIES:
    MAGICIAN = 1


class SUMMON_TYPE:
    NORMAL = 1
    SPECIAL = 2


class ATTRIBUTE:
    LIGHT = "光"
    DARK = "暗"
    FIRE = "炎"
    WATER = "水"
    EARTH = "地"
    WIND = "风"
    DIVINE = "神"


class PHASE:
    START = "开始阶段"  # draw 5
    DRAW = "抽卡阶段"
    STANDBY = "准备阶段"
    MAIN1 = "主要阶段1"
    BATTLE = "战斗阶段"
    MAIN2 = "主要阶段2"
    END = "结束阶段"
    CONSEQUENCE = {
        START: [STANDBY],
        STANDBY: [MAIN1],
        MAIN1: [BATTLE, END],
        BATTLE: [MAIN2],
        MAIN2: [END],
        END: [DRAW],
    }


class ZoneType:
    HAND = "手牌"
    MONSTER = "怪兽区"
    SPELL_TRAP = "魔陷区"
    GRAVEYARD = "墓地"
    BANISHED = "除外区"
    DECK = "卡组"
    EXTRA_DECK = "额外卡组"
    FIELD = "场地"


class ZONE:
    SELF = ZoneType
    OPPONENT = ZoneType