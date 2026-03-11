from __future__ import annotations

from dataclasses import dataclass, field

from .card import Card


@dataclass(frozen=True, slots=True)
class Player:
    id: str
    life_points: int = 8000
    hand: tuple[Card, ...] = field(default_factory=tuple)
    deck: tuple[Card, ...] = field(default_factory=tuple)
    graveyard: tuple[Card, ...] = field(default_factory=tuple)
    banished: tuple[Card, ...] = field(default_factory=tuple)
    extra_deck: tuple[Card, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "life_points": self.life_points,
            "hand": [card.to_dict() for card in self.hand],
            "deck": [card.to_dict() for card in self.deck],
            "graveyard": [card.to_dict() for card in self.graveyard],
            "banished": [card.to_dict() for card in self.banished],
            "extra_deck": [card.to_dict() for card in self.extra_deck],
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Player":
        return cls(
            id=str(data["id"]),
            life_points=int(data["life_points"]),
            hand=tuple(Card.from_dict(item) for item in data["hand"]),
            deck=tuple(Card.from_dict(item) for item in data["deck"]),
            graveyard=tuple(Card.from_dict(item) for item in data["graveyard"]),
            banished=tuple(Card.from_dict(item) for item in data["banished"]),
            extra_deck=tuple(Card.from_dict(item) for item in data["extra_deck"]),
        )
