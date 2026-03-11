from __future__ import annotations

import json
from dataclasses import dataclass

from .player import Player

SCHEMA_VERSION = "1.0"


@dataclass(frozen=True, slots=True)
class GameState:
    players: tuple[Player, Player]
    turn: int = 1
    phase: str = "DRAW"
    step: str = "START"
    priority_player: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": SCHEMA_VERSION,
            "players": [player.to_dict() for player in self.players],
            "turn": self.turn,
            "phase": self.phase,
            "step": self.step,
            "priority_player": self.priority_player,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"), sort_keys=True)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "GameState":
        version = str(data.get("schema_version", ""))
        if version != SCHEMA_VERSION:
            raise ValueError(f"Unsupported schema version: {version}")
        players = tuple(Player.from_dict(item) for item in data["players"])
        if len(players) != 2:
            raise ValueError("GameState requires exactly 2 players")
        return cls(
            players=(players[0], players[1]),
            turn=int(data["turn"]),
            phase=str(data["phase"]),
            step=str(data["step"]),
            priority_player=str(data["priority_player"]),
        )

    @classmethod
    def from_json(cls, raw: str) -> "GameState":
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("GameState JSON must decode to object")
        return cls.from_dict(data)
