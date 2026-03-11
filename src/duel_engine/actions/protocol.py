from __future__ import annotations

from dataclasses import dataclass, field

from .types import ActionType


@dataclass(frozen=True, slots=True)
class Action:
    player_id: str
    action_type: ActionType
    targets: tuple[str, ...] = field(default_factory=tuple)
    cost_info: dict[str, int | str | bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "player_id": self.player_id,
            "action_type": self.action_type.value,
            "targets": list(self.targets),
            "cost_info": dict(self.cost_info),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Action":
        raw_targets = data.get("targets", ())
        if not isinstance(raw_targets, (list, tuple)):
            raise ValueError("Action.targets must be list or tuple")

        raw_cost_info = data.get("cost_info", {})
        if not isinstance(raw_cost_info, dict):
            raise ValueError("Action.cost_info must be a dictionary")

        return cls(
            player_id=str(data["player_id"]),
            action_type=ActionType(str(data["action_type"])),
            targets=tuple(str(target) for target in raw_targets),
            cost_info={
                str(key): value
                for key, value in raw_cost_info.items()
                if isinstance(value, (int, str, bool))
            },
        )
