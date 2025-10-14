from cards.enumerations import ATTRIBUTE, CARD, RACE
from cards.models import Card


class MalissWhiteRabbit(Card):
    def __init__(self):
        super().__init__(
            name="Maliss <P> White Rabbit",
            card_type=CARD.MONSTER,
            effects=[],
            attribute=ATTRIBUTE.DARK,
            attack=1200,
            defense=300,
            level=3,
            monster_type=CARD.MONSTER.EFFECT,
            race=RACE.CYBERSE,
        )
        # effect = Effect(owner=self, index=1, effects=[], conditions=[])
        # effect.conditions.append(CardNameOnePerTurn(effect=effect))
        # effect.conditions.append(
        #     OrCombination(
        #         conditions=[
        #             CardNormalSummonOccasion(card=self),
        #             CardSpecialSummonOccasion(card=self),
        #         ]
        #     )
        # )
        # self.effects.append(effect)
