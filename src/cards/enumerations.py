from enum import Enum


class MONSTER(Enum):
    NORMAL = "通常"
    EFFECT = "效果"
    RITUAL = "仪式"
    FUSION = "融合"
    SYNCHRO = "同调"
    XYZ = "超量"
    PENDULUM = "灵摆"
    LINK = "连接"
    UNION = "同盟"
    DUAL = "二重"
    TUNER = "调整"
    TOKEN = "衍生物"
    SPSUMMON = "特殊召唤"


class SPELL(Enum):
    NORMAL = "通常"
    FIELD = "场地"
    EQUIP = "装备"
    CONTINUOUS = "永续"
    QUICKPLAY = "速攻"
    RITUAL = "仪式"


class TRAP(Enum):
    NORMAL = "通常"
    CONTINUOUS = "永续"
    COUNTER = "反击"


class CARD:
    MONSTER = MONSTER
    SPELL = SPELL
    TRAP = TRAP


class ATTRIBUTE(Enum):
    LIGHT = "光"
    DARK = "暗"
    FIRE = "炎"
    WATER = "水"
    EARTH = "地"
    WIND = "风"
    DIVINE = "神"


class RACE(Enum):
    DRAGON = "龙"
    WARRIOR = "战士"
    SPELLCASTER = "魔法师"
    FIEND = "恶魔"
    ZOMBIE = "不死"
    MACHINE = "机械"
    AQUA = "水"
    PYRO = "炎"
    ROCK = "岩石"
    PLANT = "植物"
    INSECT = "昆虫"
    THUNDER = "雷"
    FISH = "鱼"
    SEA_SERPENT = "海龙"
    REPTILE = "爬虫类"
    PSYCHO = "念动力"
    BEAST = "兽"
    BEAST_WARRIOR = "兽战士"
    DIVINE = "幻神兽"
    DINOSAUR = "恐龙"
    WYRM = "幻龙"
    CYBERSE = "电子界"
    ILLUSION = "幻想魔"


class EXPRESSION_WAY(Enum):
    ATTACK = "攻击"
    DEFENSE = "守备"
    NONE = "无"


class FACE(Enum):
    UP = "表侧"
    DOWN = "里侧"
    NONE = "无"


class SUMMON_TYPE(Enum):
    NORMAL = "通常召唤"
    SPECIAL = "特殊召唤"
    FLIP = "反转召唤"
    ADVANCE = "上级召唤"
    DUAL = "二重召唤"
    FUSION = "融合召唤"
    RITUAL = "仪式召唤"
    SYNCHRO = "同调召唤"
    XYZ = "超量召唤"
    LINK = "连接召唤"
    PENDULUM = "灵摆召唤"


class LINK_MARKER(Enum):
    TOP_LEFT = "左上"
    TOP = "上"
    TOP_RIGHT = "右上"
    LEFT = "左"
    RIGHT = "右"
    BOTTOM_LEFT = "左下"
    BOTTOM = "下"
    BOTTOM_RIGHT = "右下"
