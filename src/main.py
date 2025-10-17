from typing import List, cast

from moduvent import emit, subscribe
from ventrun import Main
from ventrun import main as run_main

from cards.MalissGWC06 import MalissGWC06
from cards.MalissWhiteRabbit import MalissWhiteRabbit
from duel.events import DuelInit
from player.models import Player


@subscribe(Main)
def main(e):
    player_1 = Player(
        name="Alice",
        main_deck=cast(
            List,
            [MalissWhiteRabbit() for _ in range(7)] + [MalissGWC06() for _ in range(3)],
        ),
        extra_deck=[],
    )
    player_2 = Player(
        name="Bob", main_deck=[MalissWhiteRabbit() for _ in range(7)], extra_deck=[]
    )
    emit(DuelInit(player_1=player_1, player_2=player_2))


if __name__ == "__main__":
    run_main()
