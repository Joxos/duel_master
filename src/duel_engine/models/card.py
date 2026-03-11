from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


def _new_card_id() -> str:
    return f"card_{uuid4().hex}"


def _new_opaque_ref() -> str:
    return f"hidden_{uuid4().hex}"


@dataclass(frozen=True, slots=True)
class Card:
    id: str = field(default_factory=_new_card_id)
    name: str = ""
    card_type: str = ""
    owner_id: str = ""
    face_up: bool = True
    opaque_ref: str = field(default_factory=_new_opaque_ref)

    def visible_identifier(self, reveal: bool) -> str:
        if reveal:
            return self.id
        return self.opaque_ref

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "id": self.id,
            "name": self.name,
            "card_type": self.card_type,
            "owner_id": self.owner_id,
            "face_up": self.face_up,
            "opaque_ref": self.opaque_ref,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str | bool]) -> "Card":
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            card_type=str(data["card_type"]),
            owner_id=str(data["owner_id"]),
            face_up=bool(data["face_up"]),
            opaque_ref=str(data["opaque_ref"]),
        )
