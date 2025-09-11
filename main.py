from duel.models import Player, Duel
from log import logger
import random


if __name__ == "__main__":
    # random card characters
    player_1 = Player(
        main_deck=[],
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
        action = random.choice(actions)
        logger.info(f"Current Phase: {duel.phase}, Action: {action}")
        duel.perform_action(action)
    logger.info(f"Duel ended. Winner: {duel.winner}")
    logger.info(f"Total Turns: {duel.turn_count}")
