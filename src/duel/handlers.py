from random import shuffle
from sys import exit

from moduvent import emit, subscribe

from actions.events import DrawCard, ShuffleDeck, Skip
from cards.enum import EXPRESSION_WAY, FACE
from cards.models import CardStatus
from duel.events import (
    DuelEnd,
    DuelInit,
    DuelStart,
    GetAndExecuteUserDecision,
    GetAvailableActions,
    GetAvailableActivations,
    InitialDraw,
    SetupCards,
)
from duel.models import Duel
from field.enum import ZoneType
from phase.events import TurnChance
from utils import cleanup_emit, show_duel_info


@subscribe(DuelInit)
def init_duel(event: DuelInit):
    duel = Duel(event.player_1, event.player_2)
    emit(DuelStart(duel=duel))


@subscribe(DuelStart)
def setup_duel(event: DuelStart):
    duel = event.duel
    emit(SetupCards(duel=duel))
    emit(ShuffleDeck(duel=duel))
    emit(InitialDraw(duel=duel))
    # we add this by hand to handle the special case of the first turn
    duel.history.append(TurnChance(duel=duel, next_player=duel.player_1))
    show_duel_info(duel=duel)
    while True:
        emit(GetAndExecuteUserDecision(duel=duel, player=duel.current_player))
        emit(GetAndExecuteUserDecision(duel=duel, player=duel.opponent_player))


@subscribe(SetupCards)
def setup_cards(event: SetupCards):
    duel, player_1, player_2 = event.duel, event.duel.player_1, event.duel.player_2
    all_decks = [
        (player_1.field.main_deck, ZoneType.MAIN_DECK, player_1),
        (player_2.field.main_deck, ZoneType.MAIN_DECK, player_2),
        (player_1.field.extra_deck, ZoneType.EXTRA_DECK, player_1),
        (player_2.field.extra_deck, ZoneType.EXTRA_DECK, player_2),
    ]

    index = 0
    for deck, zone_type, belonging in all_decks:
        for card in deck:
            card.index = index
            index += 1
            card.status = CardStatus(EXPRESSION_WAY.NONE, FACE.NONE)
            card.zone = zone_type
            card.belonging = belonging
            duel.all_cards.append(card)


@subscribe(ShuffleDeck)
def shuffle_deck(event: ShuffleDeck):
    shuffle(event.duel.player_1.field.main_deck)
    shuffle(event.duel.player_2.field.main_deck)


@subscribe(InitialDraw)
def initial_draw(event: InitialDraw):
    emit(DrawCard(duel=event.duel, player=event.duel.player_1, num=5))
    emit(DrawCard(duel=event.duel, player=event.duel.player_2, num=5))


@subscribe(DuelEnd)
def show_result(event: DuelEnd):
    show_duel_info(event.duel)
    print(f"{event.winner.name} wins the duel with {event.reason.value}!")
    exit(0)


@subscribe(GetAndExecuteUserDecision)
def get_user_decision(event: GetAndExecuteUserDecision):
    actions = cleanup_emit(
        emit(GetAvailableActions(duel=event.duel, player=event.player))
    )
    if activations := cleanup_emit(
        emit(GetAvailableActivations(duel=event.duel, player=event.player))
    ):
        activations.append(Skip(duel=event.duel, player=event.player))
    if not (actions or activations):
        emit(Skip(duel=event.duel, player=event.player))
        return

    print(f"{event.player.name}:")
    for i in range(len(actions)):
        print(f"{i + 1}. {actions[i]}")
    choice = ""
    while not (choice.isdigit() and 1 <= int(choice) <= len(actions)):
        choice = input("(choice) >>> ")
    choice = actions[int(choice) - 1]
    event.duel.history.append(choice)
    emit(choice)
    show_duel_info(event.duel)
