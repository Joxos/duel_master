# Maliss <P> White Rabbit
from duel.models import Card
from duel.enumerations import CARD, ATTRIBUTE, RACE


class MalissWhiteRabbit(Card):
    def __init__(self):
        super().__init__(
            name="Maliss <P> White Rabbit",
            card_type=CARD.MONSTER,
            attribute=ATTRIBUTE.DARK,
            attack=1200,
            defense=300,
            level=3,
            monster_type=CARD.MONSTER.EFFECT,
            race=RACE.CYBERSE,
            effects=[],
        )
