from cards.enum import CARD, NAME_FIELD
from cards.models import Card


class MalissGWC06(Card):
    def __init__(self):
        super().__init__(
            name="Maliss <C> GWC-06",
            card_type=CARD.TRAP.NORMAL,
            name_field=NAME_FIELD.MALISS,
        )
