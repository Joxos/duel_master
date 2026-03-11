from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .schema import ReplayData
from .serializer import from_json, replay_hash, to_json


@dataclass(frozen=True)
class Replay:
    data: ReplayData

    def to_json(self) -> str:
        return to_json(self.data)

    @classmethod
    def from_json(cls, payload: str) -> "Replay":
        return cls(data=from_json(payload))

    def save(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "Replay":
        source = Path(path)
        return cls.from_json(source.read_text(encoding="utf-8"))

    def replay_hash(self) -> str:
        return replay_hash(self.data)

    def verify(self, expected_hash: str) -> bool:
        return self.replay_hash() == expected_hash
