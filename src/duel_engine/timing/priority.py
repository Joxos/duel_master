from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class PriorityManager:
    players: tuple[str, str]
    current_priority_player: str
    passed_players: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if len(self.players) != 2:
            raise ValueError("PriorityManager requires exactly 2 players")
        if self.current_priority_player not in self.players:
            raise ValueError("current_priority_player must be one of players")

    def has_priority(self, player_id: str) -> bool:
        return self.current_priority_player == player_id

    def pass_priority(self, player_id: str) -> bool:
        if player_id not in self.players:
            raise ValueError(f"Unknown player_id: {player_id}")
        if not self.has_priority(player_id):
            raise ValueError("Only current priority player can pass")

        self.passed_players.add(player_id)
        if len(self.passed_players) == 2:
            return True

        other_player = (
            self.players[0] if self.players[1] == player_id else self.players[1]
        )
        self.current_priority_player = other_player
        return False

    def on_action_taken(self, next_priority_player: str) -> None:
        if next_priority_player not in self.players:
            raise ValueError(f"Unknown player_id: {next_priority_player}")
        self.current_priority_player = next_priority_player
        self.passed_players.clear()
