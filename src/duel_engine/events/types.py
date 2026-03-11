from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class EventType(Enum):
    SUMMONED = auto()
    SPECIAL_SUMMONED = auto()
    FLIPPED = auto()
    DESTROYED = auto()
    DAMAGED = auto()
    SENT_TO_GY = auto()
    BANISHED = auto()


@dataclass(frozen=True)
class Event:
    event_type: EventType
    source_card_id: str
    target_card_id: Optional[str]
    player_id: str
    timestamp: int


__all__ = ["EventType", "Event"]
