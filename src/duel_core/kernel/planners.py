from __future__ import annotations

from abc import ABC, abstractmethod

from duel_core.affairs import (
    Attack,
    Draw,
    DuelAffair,
    EnterPhase,
    ExecutableAffair,
    LpVary,
    MultiAffair,
    NormalSummon,
    SendToGraveyard,
)
from duel_core.models import DuelState


class ActionPlanner(ABC):
    @abstractmethod
    def supports(self, affair: ExecutableAffair) -> bool: ...

    @abstractmethod
    def plan(self, state: DuelState, affair: ExecutableAffair) -> DuelAffair: ...


class PassthroughPlanner(ActionPlanner):
    def __init__(self, affair_type: type[ExecutableAffair]) -> None:
        self._affair_type = affair_type

    def supports(self, affair: ExecutableAffair) -> bool:
        return isinstance(affair, self._affair_type)

    def plan(self, state: DuelState, affair: ExecutableAffair) -> DuelAffair:
        del state
        return affair


class AttackPlanner(ActionPlanner):
    def supports(self, affair: ExecutableAffair) -> bool:
        return isinstance(affair, Attack)

    def plan(self, state: DuelState, affair: ExecutableAffair) -> DuelAffair:
        if not isinstance(affair, Attack):
            raise ValueError(f"Unsupported executable: {type(affair).__name__}")

        attacker = affair.attacker
        defender_player = state.opponent_of(affair.player)
        defender = affair.defender
        children: list[DuelAffair] = []
        attacker_atk = attacker.card.atk
        if attacker_atk is None:
            raise ValueError("Attack requires attacker ATK")

        if defender is None:
            children.append(LpVary(duel=affair.duel, player=defender_player, delta=-attacker_atk))
            return MultiAffair(duel=affair.duel, requester=self.plan, children=children)

        defender_atk = defender.card.atk
        if defender_atk is None:
            raise ValueError("Attack requires defender ATK")

        if attacker_atk > defender_atk:
            children.append(
                SendToGraveyard(duel=affair.duel, player=defender_player, card=defender)
            )
            children.append(
                LpVary(
                    duel=affair.duel,
                    player=defender_player,
                    delta=-(attacker_atk - defender_atk),
                )
            )
        elif attacker_atk < defender_atk:
            children.append(SendToGraveyard(duel=affair.duel, player=affair.player, card=attacker))
            children.append(
                LpVary(
                    duel=affair.duel,
                    player=affair.player,
                    delta=-(defender_atk - attacker_atk),
                )
            )
        else:
            children.append(SendToGraveyard(duel=affair.duel, player=affair.player, card=attacker))
            children.append(
                SendToGraveyard(duel=affair.duel, player=defender_player, card=defender)
            )

        return MultiAffair(duel=affair.duel, requester=self.plan, children=children)


DEFAULT_PLANNERS: tuple[ActionPlanner, ...] = (
    AttackPlanner(),
    PassthroughPlanner(Draw),
    PassthroughPlanner(EnterPhase),
    PassthroughPlanner(NormalSummon),
)
