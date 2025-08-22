from modules.duel.models import Player, Deck
from modules.duel.handlers import DuelInitialize
from moduvent import event_manager, discover_modules


if __name__ == "__main__":
    discover_modules("modules")
    player_1 = Player(main_deck=Deck([]), extra_deck=Deck([]))
    player_2 = Player(main_deck=Deck([]), extra_deck=Deck([]))
    event_manager.emit(DuelInitialize(player_1=player_1, player_2=player_2))
