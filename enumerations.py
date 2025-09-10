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
        UNION = "同盟"
        DUAL = "二重"
        TUNER = "调整"
        TOKEN = "衍生物"
        SPSUMMON = "特殊召唤"

    class SPELL:
        NORMAL = "通常"
        FIELD = "场地"
        EQUIP = "装备"
        CONTINUOUS = "永续"
        QUICKPLAY = "速攻"
        RITUAL = "仪式"

    class TRAP:
        NORMAL = "通常"
        CONTINUOUS = "永续"
        COUNTER = "反击"


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

class RACE:
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

class PHASE:
    DRAW = "抽卡阶段"
    STANDBY = "准备阶段"
    MAIN1 = "主要阶段1"
    class BATTLE:
        START = "战斗开始"
        STEP = "战斗步骤"
        DAMAGE = "伤害步骤"
        DAMAGE_CALCULATION = "伤害计算时"
        END = "战斗阶段结束"
    MAIN2 = "主要阶段2"
    END = "结束阶段"
    CONSEQUENCE = {
        DRAW: [STANDBY],
        STANDBY: [MAIN1],
        MAIN1: [BATTLE, END],
        BATTLE: [MAIN2, END],
        MAIN2: [END],
        END: [DRAW],
    }


class ZoneType:
    HAND = "手牌"
    MONSTER_ZONE_1 = "主要怪兽区1"
    MONSTER_ZONE_2 = "主要怪兽区2"
    MONSTER_ZONE_3 = "主要怪兽区3"
    MONSTER_ZONE_4 = "主要怪兽区4"
    MONSTER_ZONE_5 = "主要怪兽区5"
    EXTRA_MONSTER_ZONE_1 = "额外怪兽区1"
    EXTRA_MONSTER_ZONE_2 = "额外怪兽区2"
    SPELL_TRAP_ZONE_1 = "魔陷区1"
    SPELL_TRAP_ZONE_2 = "魔陷区2"
    SPELL_TRAP_ZONE_3 = "魔陷区3"
    SPELL_TRAP_ZONE_4 = "魔陷区4"
    SPELL_TRAP_ZONE_5 = "魔陷区5"
    FIELD_ZONE = "场地区"
    GRAVEYARD = "墓地"
    BANISHED = "除外区"
    DECK = "卡组"
    EXTRA_DECK = "额外卡组"
    FIELD = "场地"
    REMOVED = "除外"
    OVERLAY = "超量素材"


class ZONE:
    SELF = ZoneType
    OPPONENT = ZoneType

class CARD_STATUS:
    class POSITION:
        ATTACK = "攻击"
        DEFENSE = "守备"
        
    class FACE:
        UP = "表侧"
        DOWN = "里侧"

class END_REASON:
    LIFE_POINTS = "生命值归零"
    DECK_OUT = "卡组耗尽"
    SURRENDER = "认输"
    TIME_OUT = "时间到"

class UNIT:
    TURN = "回合"
    DUEL = "决斗"

class CHECK_TYPE:
    CARD = "卡片"
    NAME = "卡名"

class SUMMON_TYPE:
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

class LINK_MARKER:
    TOP_LEFT = "左上"
    TOP = "上"
    TOP_RIGHT = "右上"
    LEFT = "左"
    RIGHT = "右"
    BOTTOM_LEFT = "左下"
    BOTTOM = "下"
    BOTTOM_RIGHT = "右下"