from __future__ import annotations

from typing import NotRequired, TypedDict


class CardData(TypedDict):
    id: str
    name: str
    type: str
    effect_text: str
    spell_speed: NotRequired[int]


MALISS_CORE6_CARDS: tuple[CardData, ...] = (
    {
        "id": "MALISS-P-WHITE-RABBIT",
        "name": "M∀LICE＜P＞White Rabbit",
        "type": "Monster",
        "effect_text": 'If this card is Normal or Special Summoned: You can Set 1 "M∀LICE" Trap directly from your Deck. If this card is banished: You can pay 300 LP; Special Summon this card, then you can banish 1 "M∀LICE" card from your hand or Deck.',
    },
    {
        "id": "MALISS-P-CHESHIRE-CAT",
        "name": "M∀LICE＜P＞Cheshire Cat",
        "type": "Monster",
        "effect_text": 'You can banish 1 other "M∀LICE" card from your hand or face-up field; Special Summon this card from your hand. If this card is banished: You can pay 300 LP; Special Summon this card, then you can send 1 "M∀LICE" card from your Deck to the GY.',
    },
    {
        "id": "MALISS-P-MARCH-HARE",
        "name": "M∀LICE＜P＞March Hare",
        "type": "Monster",
        "effect_text": 'During your Main Phase, if this card is in your hand and your opponent controls a monster: You can banish 1 other "M∀LICE" card from your hand or GY; Special Summon this card. If this card is banished: You can pay 300 LP; Special Summon this card, then you can add 1 of your banished "M∀LICE" cards to your hand.',
    },
    {
        "id": "MALISS-P-DORMOUSE",
        "name": "M∀LICE＜P＞Dormouse",
        "type": "Monster",
        "effect_text": 'You can target 1 "M∀LICE" monster you control; banish 1 "M∀LICE" monster from your Deck with a different name from that monster, and if you do, this card\'s name becomes that banished monster\'s name until the End Phase. If this card is banished: You can pay 300 LP; Special Summon this card.',
    },
    {
        "id": "MALISS-IN-UNDERGROUND",
        "name": "M∀LICE IN UNDERGROUND",
        "type": "Field Spell",
        "effect_text": 'When this card is activated: You can add 1 "M∀LICE" monster from your Deck to your hand. Once per turn, if your "M∀LICE" monster is banished, except during the Damage Step: You can banish 1 card from your hand, then draw 2 cards. During your Main Phase: You can Link Summon 1 "M∀LICE" Link Monster using monsters you control.',
        "spell_speed": 1,
    },
    {
        "id": "MALISS-C-MTP-07",
        "name": "M∀LICE＜C＞MTP－０７",
        "type": "Trap",
        "effect_text": 'If you control a "M∀LICE" Link Monster: Target 1 card your opponent controls; banish it. If this Set card is banished by your card effect: You can Set this card. You can only use each effect of "M∀LICE＜C＞MTP－０７" once per turn.',
        "spell_speed": 2,
    },
)


def get_maliss_core6_cards() -> tuple[CardData, ...]:
    return MALISS_CORE6_CARDS
