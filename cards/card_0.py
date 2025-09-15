# Maliss <P> White Rabbit
from duel.models import Card, Effect
from duel.enumerations import CARD, ATTRIBUTE, RACE
from duel.actions import CardNameOnePerTurn


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
        effect = Effect(owner=self, index=1, effects=[], conditions=[])
        effect.conditions.append(CardNameOnePerTurn(effect=effect))
        self.effects.append(effect)
