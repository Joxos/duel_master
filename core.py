from components.components import Duel, Player, Deck
from actions import NextPhase, show_actions
from events import EventsManager

MODULE_LIST = []
EVENT_LIST = []

class Game:
    def __init__(self, player_1: Player, player_2: Player):
        self.duel = Duel(player_1, player_2)
        self.events_manager = EventsManager()
        self.events_manager.set_game_ref(self.duel)
        self.events_manager.register(EVENT_LIST)
        self.events_manager.import_modules(MODULE_LIST)