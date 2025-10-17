from moduvent import emit, subscribe

from actions.events import DrawCard, MoveCard, NormalSummon, PostPhase, SetPhase
from cards.enum import CARD, EXPRESSION_WAY, FACE
from cards.models import CardStatus
from duel.enum import END_REASON
from duel.events import DuelEnd, GetAvailableActions
from field.enum import ZoneType
from field.models import Location
from phase.enum import CONSEQUENCE, CONSEQUENCE_OF_TURN_1, PHASE
from phase.models import PhaseWithPlayer
from utils import select_main_field


@subscribe(SetPhase)
def set_phase(event: SetPhase):
    duel, phase = event.duel, event.phase
    emit(PostPhase(duel=duel, phase=phase))
    duel.phase = phase


@subscribe(GetAvailableActions)
def normal_summon_available(event: GetAvailableActions):
    duel, player = event.duel, event.player
    player_correct = duel.current_player == player
    phase_correct = duel.current_phase in [PHASE.MAIN1, PHASE.MAIN2]
    has_zone = not all(player.field.main_monster_zones)
    first_time = not any(
        isinstance(action, NormalSummon)
        for action in duel.history.current_turn_actions()
    )
    if player_correct and phase_correct and has_zone and first_time:
        return [
            NormalSummon(duel=duel, player=player, card=card)
            for card in player.field.hands
            if card.card_type in [CARD.MONSTER.NORMAL, CARD.MONSTER.EFFECT]
            and card.level
            and card.level <= 4
        ]
    return []


@subscribe(NormalSummon)
def normal_summon(event: NormalSummon):
    player, card = event.player, event.card
    zone_index = ""
    while not (
        zone_index.isdigit()
        and 0 < int(zone_index) <= 5
        and player.field.main_monster_zones[int(zone_index) - 1] is None
    ):
        zone_index = input("(zone_index) >>> ")
    zone_index = int(zone_index) - 1
    card.status = CardStatus(position=EXPRESSION_WAY.ATTACK, face=FACE.UP)
    card.zone = Location(
        player=player, zone=ZoneType(ZoneType.MAIN_MONSTER_ZONE.value[zone_index])
    )
    player.field.main_monster_zones[zone_index] = card
    player.field.hands.remove(card)


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


@subscribe(MoveCard)
def move_card(event: MoveCard):
    card, from_zone, to_zone = event.card, event.from_zone, event.to_zone

    if None in [card, from_zone, to_zone]:
        raise ValueError(
            f"Moving card={card}, from_zone={from_zone}, to_zone={to_zone} is not valid."
        )

    if from_zone.zone in [ZoneType.MAIN_MONSTER_ZONE, ZoneType.SPELL_TRAP_ZONE]:
        zone_index = select_main_field(from_zone.player.field, from_zone.zone)
        from_zone.player.field.convert[from_zone.zone][zone_index] = None
    elif from_zone == ZoneType.FIELD_ZONE:
        from_zone.player.field.field_zone = None
    else:
        from_zone.player.field.convert[from_zone.zone].remove(card)

    if to_zone.zone in [ZoneType.MAIN_MONSTER_ZONE, ZoneType.SPELL_TRAP_ZONE]:
        zone_index = select_main_field(to_zone.player.field, to_zone.zone)
        to_zone.player.field.convert[to_zone.zone][zone_index] = card
    elif to_zone == ZoneType.FIELD_ZONE:
        to_zone.player.field.field_zone = card
    else:
        to_zone.player.field.convert[to_zone.zone].append(card)
