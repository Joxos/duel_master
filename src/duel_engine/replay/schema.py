from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

REPLAY_SCHEMA_VERSION = "replay.v0"


@dataclass(frozen=True)
class ReplayData:
    engine_version: str
    ruleset_id: str
    seed: int
    initial_state_hash: str
    actions: list[dict[str, Any]] = field(default_factory=list)
    choices: list[dict[str, Any]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    schema_version: str = REPLAY_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "engine_version": self.engine_version,
            "ruleset_id": self.ruleset_id,
            "seed": self.seed,
            "initial_state_hash": self.initial_state_hash,
            "actions": list(self.actions),
            "choices": list(self.choices),
            "events": list(self.events),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ReplayData":
        schema_version = payload.get("schema_version", REPLAY_SCHEMA_VERSION)
        if schema_version != REPLAY_SCHEMA_VERSION:
            raise ValueError(
                f"unsupported replay schema version: {schema_version!r}; expected {REPLAY_SCHEMA_VERSION!r}"
            )

        return cls(
            schema_version=schema_version,
            engine_version=str(payload["engine_version"]),
            ruleset_id=str(payload["ruleset_id"]),
            seed=int(payload["seed"]),
            initial_state_hash=str(payload["initial_state_hash"]),
            actions=[dict(item) for item in payload.get("actions", [])],
            choices=[dict(item) for item in payload.get("choices", [])],
            events=[dict(item) for item in payload.get("events", [])],
        )
