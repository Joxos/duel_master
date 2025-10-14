from moduvent import emit, subscribe
from ventrun import Main

from cards.MalissWhiteRabbit import MalissWhiteRabbit
from duel.events import DuelInit
from player.models import Player


@subscribe(Main)
def main(e):
    player_1 = Player(
        name="Alice", main_deck=[MalissWhiteRabbit() for _ in range(5)], extra_deck=[]
    )
    player_2 = Player(
        name="Bob", main_deck=[MalissWhiteRabbit() for _ in range(5)], extra_deck=[]
    )
    emit(DuelInit(player_1=player_1, player_2=player_2))
