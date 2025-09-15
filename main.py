from duel.models import Player, Duel
from duel.actions import show_action
from duel.enumerations import FACE
from cards.card_0 import MalissWhiteRabbit
from log import logger


def show_field(duel: Duel):
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

    turn_info = f"回合: {duel.turn_count} 阶段: {duel.phase.phase} 当前玩家: {duel.phase.player}"
    print(turn_info.center(100))
    print("=" * 100)

    lines = []

    p2_main_deck = format_count(f"主卡组:{len(p2.main_deck)}")
    p2_hand = format_count(f"手卡:{len(p2.hand)}")
    p2_extra = format_count(f"额外:{len(p2.extra_deck)}")
    lines.append(f"{p2_main_deck} {p2_hand} {p2_extra}")

    p2_grave = format_count(f"墓地:{len(p2.graveyard)}")
    p2_spell_trap = [format_card(card) for card in p2.spell_trap_zone]
    p2_field = format_card(p2.field_zone[0])
    lines.append(f"{p2_grave} {' '.join(p2_spell_trap)} {p2_field}")

    p2_banish = format_count(f"除外:{len(p2.banished)}")
    p2_monsters = [format_card(card) for card in p2.main_monster_zone]
    lines.append(f"{p2_banish} {' '.join(p2_monsters)}")

    extra_monsters = [format_card(card) for card in duel.extra_monster_zone]
    middle_pos = (len(lines[2]) - (ZONE_WIDTH * 2 + 1)) // 2
    lines.append(" " * middle_pos + " ".join(extra_monsters))

    p1_monsters = [format_card(card) for card in p1.main_monster_zone]
    p1_banish = format_count(f"除外:{len(p1.banished)}")
    p1_line = " ".join(p1_monsters) + " " + p1_banish
    lines.append(p1_line.rjust(len(lines[2])))

    p1_field = format_card(p1.field_zone[0])
    p1_spell_trap = [format_card(card) for card in p1.spell_trap_zone]
    p1_grave = format_count(f"墓地:{len(p1.graveyard)}")
    p1_line = f"{p1_field} {' '.join(p1_spell_trap)} {p1_grave}"
    lines.append(p1_line.rjust(len(lines[1])))

    p1_extra = format_count(f"额外:{len(p1.extra_deck)}")
    p1_hand = format_count(f"手卡:{len(p1.hand)}")
    p1_main_deck = format_count(f"主卡组:{len(p1.main_deck)}")
    p1_line = f"{p1_extra} {p1_hand} {p1_main_deck}"
    lines.append(p1_line.rjust(len(lines[0])))

    print(f"玩家2手牌: {', '.join([card.name for card in p2.hand])}")
    for line in lines:
        print(line)
    print(f"玩家1手牌: {', '.join([card.name for card in p1.hand])}")


if __name__ == "__main__":
    # random card characters
    player_1 = Player(
        main_deck=[MalissWhiteRabbit()],
        extra_deck=[],
    )
    player_2 = Player(
        main_deck=[],
        extra_deck=[],
    )
    duel = Duel(player_1, player_2)
    duel.setup()
    duel.draw_card(player_1, 1)
    while not duel.winner:
        show_field(duel)
        actions = duel.available_actions()
        if not actions:
            logger.info("No available actions, ending duel.")
            break
        show_action(actions)
        action_index = input("Choose an action index: ")
        try:
            action_index = int(action_index)
            action = actions[action_index]
        except (ValueError, IndexError):
            logger.warning("Invalid action index, please try again.")
            continue
        action.perform()
    logger.info(f"Duel ended. Winner: {duel.winner}")
    logger.info(f"Total Turns: {duel.turn_count}")
