from modules import discover_modules
from modules.duel import Player, Deck
from modules.duel.handlers import DuelInitialize
from events import event_manager

if __name__ == "__main__":
    discover_modules()
    player_1 = Player(main_deck=Deck([]), extra_deck=Deck([]))
    player_2 = Player(main_deck=Deck([]), extra_deck=Deck([]))
    event_manager.emit(DuelInitialize(player_1=player_1, player_2=player_2))
