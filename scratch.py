from core import Duel, Player, Deck
from actions import NextPhase, show_actions

player_1_main_deck = Deck()
player_1_extra_deck = Deck()
player_1 = Player(main_deck=player_1_main_deck, extra_deck=player_1_extra_deck)
player_2_main_deck = Deck()
player_2_extra_deck = Deck()
player_2 = Player(main_deck=player_2_main_deck, extra_deck=player_2_extra_deck)
duel = Duel(player_1, player_2)

while True:
    actions = duel.available_actions()
    show_actions(actions)
    choice = input("Choose an action: ")
    if choice.isdigit() and 0 <= int(choice) < len(actions):
        selected_action = actions[int(choice)]
        duel.perform_action(selected_action)
    else:
        print("Invalid choice. Please try again.")