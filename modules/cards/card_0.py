# Live⭐Twin Lil-la
from ..duel.models import SimpleMonsterCard, Effect
from enumerations import CARD, ATTRIBUTE, SPECIES

class LiveTwinLilla(SimpleMonsterCard):
    def __init__(self):
        super().__init__(
            name="Live☆Twin Lil-la",
            card_type=CARD.MONSTER,
            attribute=ATTRIBUTE.DARK,
            attack=500,
            defense=0,
            level=2,
            monster_type=CARD.MONSTER.EFFECT,
            species=SPECIES.FIEND,
            effects=[]
        )