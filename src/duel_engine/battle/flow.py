from __future__ import annotations

from dataclasses import dataclass

from .damage_step import DamageStepMachine


@dataclass(slots=True)
class BattleFlow:
    player_life_points: dict[str, int]
    damage_step_machine: DamageStepMachine

    attacker: dict[str, object] | None = None
    defender: dict[str, object] | None = None
    pending_damage: dict[str, int] | None = None

    def __init__(self, player_life_points: dict[str, int]) -> None:
        self.player_life_points = dict(player_life_points)
        self.damage_step_machine = DamageStepMachine()
        self.attacker = None
        self.defender = None
        self.pending_damage = None

    def declare_attack(
        self, attacker: dict[str, object], defender: dict[str, object] | None
    ) -> None:
        attack_value = int(attacker.get("attack", 0))
        if attack_value < 0:
            raise ValueError("Attacker attack value cannot be negative")

        if defender is not None:
            defend_value = int(defender.get("attack", 0))
            if defend_value < 0:
                raise ValueError("Defender attack value cannot be negative")

        self.attacker = attacker
        self.defender = defender
        self.pending_damage = None
        self.damage_step_machine = DamageStepMachine()

    def calculate_damage(
        self,
        attacker: dict[str, object] | None = None,
        defender: dict[str, object] | None = None,
    ) -> dict[str, int]:
        active_attacker = attacker or self.attacker
        active_defender = defender if defender is not None else self.defender

        if active_attacker is None:
            raise ValueError("Cannot calculate damage before attack declaration")

        attacker_controller = str(active_attacker["controller"])
        attacker_attack = int(active_attacker.get("attack", 0))

        if attacker_attack < 0:
            raise ValueError("Attacker attack value cannot be negative")

        damage = {player_id: 0 for player_id in self.player_life_points}

        if active_defender is None:
            opponent = self._opponent_of(attacker_controller)
            damage[opponent] = attacker_attack
        else:
            defender_controller = str(active_defender["controller"])
            defender_attack = int(active_defender.get("attack", 0))
            if defender_attack < 0:
                raise ValueError("Defender attack value cannot be negative")

            if attacker_attack > defender_attack:
                damage[defender_controller] = attacker_attack - defender_attack
            elif defender_attack > attacker_attack:
                damage[attacker_controller] = defender_attack - attacker_attack

        self.attacker = active_attacker
        self.defender = active_defender
        self.pending_damage = damage
        return damage

    def resolve_battle(self) -> dict[str, int]:
        if self.pending_damage is None:
            raise ValueError("Cannot resolve battle before damage calculation")

        for player_id, amount in self.pending_damage.items():
            current_lp = self.player_life_points[player_id]
            self.player_life_points[player_id] = max(0, current_lp - amount)

        result = dict(self.player_life_points)
        self.pending_damage = None
        self.attacker = None
        self.defender = None
        return result

    def _opponent_of(self, player_id: str) -> str:
        players = tuple(self.player_life_points.keys())
        if player_id not in players:
            raise ValueError(f"Unknown player_id: {player_id}")
        for candidate in players:
            if candidate != player_id:
                return candidate
        raise ValueError("BattleFlow requires exactly two players")
