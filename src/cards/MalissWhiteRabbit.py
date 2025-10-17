from moduvent import emit

from actions.events import MoveCard, NormalSummon
from cards.enum import ATTRIBUTE, CARD, EXPRESSION_WAY, FACE, NAME_FIELD, RACE
from cards.models import Card, CardStatus
from duel.events import GetAvailableActivations
from effects.enum import CHECK_TYPE, UNIT
from effects.events import Activate, Activation
from effects.models import Times
from field.enum import ZoneType
from field.models import Location
from utils import select_range


class MalissWhiteRabbit(Card):
    def __init__(self):
        super().__init__(
            name="Maliss <P> White Rabbit",
            card_type=CARD.MONSTER.EFFECT,
            attribute=ATTRIBUTE.DARK,
            effects={1: (self.effect_1_available, self.effect_1)},
            attack=1200,
            defense=300,
            level=3,
            monster_type=CARD.MONSTER.EFFECT,
            race=RACE.CYBERSE,
            name_field=NAME_FIELD.MALISS,
        )

    def effect_1_available(self, event: GetAvailableActivations):
        if (
            NormalSummon(duel=event.duel, player=event.player, card=self)
            in event.duel.history.current_occasions()
            and Times(
                unit=UNIT.TURN,
                check_type=CHECK_TYPE.NAME,
                counts=1,
            ).available(event, self)
            and any(
                card.name_field == NAME_FIELD.MALISS
                and card.card_type in CARD.TRAP
                and card not in event.player.field.graveyard
                for card in event.player.field.main_deck
            )
        ):
            return [Activate(duel=event.duel, card=self, index=1, player=event.player)]

    def effect_1(self, event: Activate):
        # costs
        emit(Activation(duel=event.duel, card=self, index=1, player=event.player))
        if candidates := [
            card
            for card in event.player.field.main_deck
            if card.name_field == NAME_FIELD.MALISS
            and card.card_type in CARD.TRAP
            and card not in event.player.field.graveyard
        ]:
            print(f"{event.player.name}:")
            for i in range(len(candidates)):
                print(f"{i + 1}. {candidates[i]}")
            choice = candidates[select_range(1, len(candidates), "Maliss Trap")]
            choice.status = CardStatus(position=EXPRESSION_WAY.ATTACK, face=FACE.DOWN)
            action = MoveCard(
                duel=event.duel,
                card=choice,
                from_zone=Location(player=event.player, zone=ZoneType.MAIN_DECK),
                to_zone=Location(player=event.player, zone=ZoneType.SPELL_TRAP_ZONE),
            )
            event.duel.history.append(action)
            emit(action)
