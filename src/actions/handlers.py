from moduvent import emit, subscribe

from actions.events import DrawCard, NormalSummon, SetPhase
from cards.enum import EXPRESSION_WAY, FACE
from cards.models import CardStatus
from duel.enum import END_REASON
from duel.events import DuelEnd, GetAvailableActions
from phase.enum import CONSEQUENCE, CONSEQUENCE_OF_TURN_1, PHASE
from phase.models import PhaseWithPlayer
from utils import show_duel_info


@subscribe(SetPhase)
def set_phase(event: SetPhase):
    duel, phase = event.duel, event.phase
    duel.phase = phase
    show_duel_info(duel)


@subscribe(GetAvailableActions)
def normal_summon_available(event: GetAvailableActions):
    duel, player = event.duel, event.player
    player_correct = duel.current_player == player
    phase_correct = duel.current_phase in [PHASE.MAIN1, PHASE.MAIN2]
    if player_correct and phase_correct:
        for action in duel.history.current_turn():
            if isinstance(action, NormalSummon):
                return []
        available_hands = [
            card for card in player.field.hands if card.level and card.level <= 4
        ]
        return [
            NormalSummon(duel=duel, player=player, card=card)
            for card in available_hands
        ]
    return []


# @subscribe(GetAvailableActions)
# def skip(event: GetAvailableActions):
#     return [Skip(duel=event.duel)]


@subscribe(NormalSummon)
def normal_summon(event: NormalSummon):
    duel, player, card = event.duel, event.player, event.card
    zone_index = ""
    while not (zone_index.isdigit() and 0 < int(zone_index) <= 5):
        zone_index = input("(zone_index) >>> ")
    card.status = CardStatus(position=EXPRESSION_WAY.ATTACK, face=FACE.UP)
    player.field.main_monster_zones[int(zone_index) - 1] = card
    player.field.hands.remove(card)
    show_duel_info(duel)


@subscribe(GetAvailableActions)
def change_phase(event: GetAvailableActions):
    duel, player = event.duel, event.player
    if duel.current_player == player:
        actions = []
        consequence = CONSEQUENCE if duel.turn_count != 1 else CONSEQUENCE_OF_TURN_1
        for phase in consequence[duel.current_phase]:
            player = player if phase != PHASE.DRAW else duel.other_player(player)
            actions.append(
                SetPhase(duel=duel, phase=PhaseWithPlayer(phase=phase, player=player))
            )
        return actions
    return []


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
                    winner=duel.other_player(player),
                )
            )
