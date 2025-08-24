from modules.duel.models import Player, Deck, Card
from modules.duel.handlers import DuelInitialize
from moduvent import event_manager, discover_modules
import random
import string


def generate_random_string(length=10):
    chars = []
    for _ in range(length):
        char = random.choice(string.ascii_letters)
        chars.append(char)
    return "".join(chars)


if __name__ == "__main__":
    discover_modules("modules")
    # random card characters
    player_1 = Player(
        main_deck=Deck([Card(generate_random_string(), None, None) for _ in range(40)]),
        extra_deck=Deck([]),
    )
    player_2 = Player(
        main_deck=Deck([Card(generate_random_string(), None, None) for _ in range(40)]),
        extra_deck=Deck([]),
    )
    event_manager.emit(DuelInitialize(player_1=player_1, player_2=player_2))
