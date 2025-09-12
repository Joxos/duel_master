from duel.models import Player, Duel
from duel.actions import show_action
from cards.card_0 import MalissWhiteRabbit
from log import logger


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
    while not duel.winner:
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
        action.perform(duel)
    logger.info(f"Duel ended. Winner: {duel.winner}")
    logger.info(f"Total Turns: {duel.turn_count}")
