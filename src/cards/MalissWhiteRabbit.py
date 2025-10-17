from actions.events import NormalSummon
from cards.enum import ATTRIBUTE, CARD, NAME_FIELD, RACE
from cards.models import Card
from duel.events import GetAvailableActivations
from effects.enum import CHECK_TYPE, UNIT
from effects.models import Times


class MalissWhiteRabbit(Card):
    def __init__(self):
        super().__init__(
            name="Maliss <P> White Rabbit",
            card_type=CARD.MONSTER.EFFECT,
            attribute=ATTRIBUTE.DARK,
            effects={1: self.effect_1},
            attack=1200,
            defense=300,
            level=3,
            monster_type=CARD.MONSTER.EFFECT,
            race=RACE.CYBERSE,
            name_field=NAME_FIELD.MALISS,
        )

    def effect_1_available(self, event: GetAvailableActivations):
        return (
            (
                NormalSummon(duel=event.duel, player=event.player, card=self)
                in event.duel.history.current_occasions()
            )
            and Times(
                unit=UNIT.TURN,
                check_type=CHECK_TYPE.NAME,
                counts=1,
            ).available(event, self)
            and any(
                [
                    card.name_field == NAME_FIELD.MALISS
                    and card not in event.player.field.graveyard
                    for card in event.player.field.main_deck
                ]
            )
        )

    def effect_1(self):
        # emit(Activation(duel=event.duel, card=self, index=1))
        pass
