from typing import TYPE_CHECKING

from cards.enumerations import FACE

if TYPE_CHECKING:
    from duel.models import Duel


def show_duel_info(duel: "Duel"):
    p1 = duel.player_1
    p2 = duel.player_2

    ZONE_WIDTH = 15
    COUNT_WIDTH = 8

    def format_zone(content, width=ZONE_WIDTH):
        return str(content).ljust(width)[:width]

    def format_count(count, width=COUNT_WIDTH):
        return str(count).rjust(width)

    def format_card(card):
        if card is None:
            return format_zone("[   ]")
        if hasattr(card, "status") and card.status.face != FACE.UP:
            return format_zone("里侧")
        return format_zone(card.name)

    turn_info = f"回合: {duel.turn_count} 阶段: {duel.phase.phase} 当前玩家: {duel.phase.player.name}"
    print(turn_info.center(100))
    print("=" * 100)

    lines = []

    p2_main_deck = format_count(f"主卡组:{len(p2.field.main_deck)}")
    p2_hand = format_count(f"手卡:{len(p2.field.hands)}")
    p2_extra = format_count(f"额外:{len(p2.field.extra_deck)}")
    lines.append(f"{p2_main_deck} {p2_hand} {p2_extra}")

    p2_grave = format_count(f"墓地:{len(p2.field.graveyard)}")
    p2_spell_trap = [format_card(card) for card in p2.field.spell_trap_zones]
    p2_field = format_card(p2.field.field_zone)
    lines.append(f"{p2_grave} {' '.join(p2_spell_trap)} {p2_field}")

    p2_banish = format_count(f"除外:{len(p2.field.banished)}")
    p2_monsters = [format_card(card) for card in p2.field.main_monster_zones]
    lines.append(f"{p2_banish} {' '.join(p2_monsters)}")

    extra_monsters = [format_card(card) for card in duel.extra_monster_zones]
    middle_pos = (len(lines[2]) - (ZONE_WIDTH * 2 + 1)) // 2
    lines.append(" " * middle_pos + " ".join(extra_monsters))

    p1_monsters = [format_card(card) for card in p1.field.main_monster_zones]
    p1_banish = format_count(f"除外:{len(p1.field.banished)}")
    p1_line = " ".join(p1_monsters) + " " + p1_banish
    lines.append(p1_line.rjust(len(lines[2])))

    p1_field = format_card(p1.field.field_zone)
    p1_spell_trap = [format_card(card) for card in p1.field.spell_trap_zones]
    p1_grave = format_count(f"墓地:{len(p1.field.graveyard)}")
    p1_line = f"{p1_field} {' '.join(p1_spell_trap)} {p1_grave}"
    lines.append(p1_line.rjust(len(lines[1])))

    p1_extra = format_count(f"额外:{len(p1.field.extra_deck)}")
    p1_hand = format_count(f"手卡:{len(p1.field.hands)}")
    p1_main_deck = format_count(f"主卡组:{len(p1.field.main_deck)}")
    p1_line = f"{p1_extra} {p1_hand} {p1_main_deck}"
    lines.append(p1_line.rjust(len(lines[0])))

    print(f"玩家2手牌: {', '.join([card.name for card in p2.field.hands])}")
    for line in lines:
        print(line)
    print(f"玩家1手牌: {', '.join([card.name for card in p1.field.hands])}")
