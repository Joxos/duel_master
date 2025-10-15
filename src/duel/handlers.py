from random import shuffle
from sys import exit

from moduvent import emit, subscribe

from actions.events import DrawCard, SetPhase, ShuffleDeck
from duel.enum import END_REASON
from duel.events import DuelEnd, DuelInit, DuelStart, InitialDraw
from duel.models import Duel
from duel.utils import show_duel_info
from phase.enum import PHASE
from phase.models import PhaseWithPlayer


@subscribe(DuelInit)
def init_duel(event: DuelInit):
    duel = Duel(event.player_1, event.player_2)
    emit(DuelStart(duel=duel))


@subscribe(DuelStart)
def setup_duel(event: DuelStart):
    emit(ShuffleDeck(duel=event.duel))
    emit(InitialDraw(duel=event.duel))
    emit(SetPhase(duel=event.duel, phase=PhaseWithPlayer(phase=PHASE.STANDBY, player=event.duel.player_1)))


@subscribe(ShuffleDeck)
def shuffle_deck(event: ShuffleDeck):
    shuffle(event.duel.player_1.field.main_deck)
    shuffle(event.duel.player_2.field.main_deck)


@subscribe(InitialDraw)
def initial_draw(event: InitialDraw):
    emit(DrawCard(duel=event.duel, player=event.duel.player_1, num=5))
    emit(DrawCard(duel=event.duel, player=event.duel.player_2, num=5))


@subscribe(DrawCard)
def draw_card(event: DrawCard):
    player, num, duel = event.player, event.num, event.duel
    for _ in range(num):
        if player.field.main_deck:
            card = player.field.main_deck.pop()
            player.field.hands.append(card)
        else:
            emit(
                DuelEnd(
                    duel=event.duel,
                    reason=END_REASON.DECK_OUT,
                    winner=duel.opponent_player(player),
                )
            )


@subscribe(DuelEnd)
def show_result(event: DuelEnd):
    show_duel_info(event.duel)
    print(f"{event.winner.name} wins the duel with {event.reason.value}!")
    exit(0)
