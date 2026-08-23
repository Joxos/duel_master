"""Execution kernel for the current duel slice.

This module owns runtime state mutation, guarded execution, and the execution
loop that emits completion back into the affair graph.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from affairon import Dispatcher

from duel_core.affairs import (
    ActionableDuelAffair,
    Attack,
    CompletedAffair,
    Draw,
    DuelAffair,
    ExecutableAffair,
    EnterPhase,
    ExecutionRequest,
    Forbid,
    LpVary,
    MatchEnd,
    MultiAffair,
    NormalSummon,
    SendToGraveyard,
    TurnCleanup,
)
from duel_core.models import DuelState, Player, RuntimeCard, REPRESENTATION
from duel_core.phase import Phase

if TYPE_CHECKING:
    from duel_core.duel import Duel


class Kernel:
    """Runtime execution owner for the current duel slice.

    Attributes:
        state: Kernel-owned runtime duel state.
        supported_actions: Guarded affairs executable by the kernel.
    """

    def __init__(self, state: DuelState) -> None:
        self.state = state
        self._forbids: list[Forbid] = []
        self.dispatcher = Dispatcher()

    def register(self, duel_dispatcher: Dispatcher) -> None:
        duel_dispatcher.on(ExecutionRequest)(self._execute_request)
        duel_dispatcher.on(Draw)(self._execute_top_level)
        duel_dispatcher.on(EnterPhase)(self._execute_top_level)
        duel_dispatcher.on(NormalSummon)(self._execute_top_level)
        duel_dispatcher.on(Attack)(self._execute_top_level)
        duel_dispatcher.on(Forbid)(self._register_forbid)
        duel_dispatcher.on(TurnCleanup)(self._cleanup_forbids)
        duel_dispatcher.on(MatchEnd)(self._apply_match_end)

    def is_forbidden(self, affair: ActionableDuelAffair) -> bool:
        return any(
            forbid.target == affair and forbid.outdated_when.turn >= self.state.current_turn
            for forbid in self._forbids
        )

    def _execute_request(self, affair: ExecutionRequest) -> None:
        self._run_top_level(affair.duel, affair.affair)

    def _execute_top_level(self, affair: ExecutableAffair) -> None:
        self._run_top_level(affair.duel, affair)

    def _run_top_level(self, duel: Duel, action: ExecutableAffair) -> None:
        if self.is_forbidden(action):
            raise ValueError(f"Forbidden: {type(action).__name__}")
        result = self._plan_result(action)
        self._apply_result(duel, result)
        duel.dispatcher.emit(CompletedAffair(duel=duel, action=action, result=result))

    def _plan_result(self, affair: ExecutableAffair) -> DuelAffair:
        match affair:
            case Attack():
                return self._plan_attack(affair)
            case Draw() | EnterPhase() | NormalSummon():
                return affair
            case _:
                raise ValueError(f"Unsupported executable: {type(affair).__name__}")

    def _apply_draw(self, affair: Draw) -> None:
        drawn = affair.player.main_deck.cards[: affair.num]
        del affair.player.main_deck.cards[: affair.num]
        affair.player.hand.extend(RuntimeCard(card=c) for c in drawn)

    def _apply_enter_phase(self, affair: EnterPhase) -> None:
        if affair.phase is Phase.END:
            self._advance_to_next_turn(affair)
            return
        self.state.phase = affair.phase

    def _apply_normal_summon(self, affair: NormalSummon) -> None:
        if self.state.normal_summon_used:
            raise ValueError("Normal summon already used this turn")
        empty_zone = affair.player.monster_zones.index(None)
        hand_index = affair.player.hand.index(affair.card)
        affair.player.monster_zones[empty_zone] = affair.player.hand.pop(hand_index)
        affair.card.representation = REPRESENTATION.ATTACK
        self.state.normal_summon_used = True

    def _plan_attack(self, affair: Attack) -> MultiAffair:
        attacker = affair.attacker
        defender_player = self.state.opponent_of(affair.player)
        defender = affair.defender
        children: list[DuelAffair] = []
        attacker_atk = attacker.card.atk
        if attacker_atk is None:
            raise ValueError("Attack requires attacker ATK")

        if defender is None:
            children.append(LpVary(duel=affair.duel, player=defender_player, delta=-attacker_atk))
            return MultiAffair(
                duel=affair.duel,
                requester=self._plan_attack,
                children=children,
            )

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

        return MultiAffair(
            duel=affair.duel,
            requester=self._plan_attack,
            children=children,
        )

    def _apply_send_to_graveyard(self, affair: SendToGraveyard) -> None:
        zone_index = affair.player.monster_zones.index(affair.card)
        affair.player.monster_zones[zone_index] = None
        affair.card.representation = REPRESENTATION.VOID
        affair.player.graveyard.append(affair.card)

    def _apply_lp_vary(self, affair: LpVary) -> None:
        affair.player.life_points += affair.delta

    def _apply_match_end(self, affair: MatchEnd) -> None:
        if self.state.game_over:
            return
        self._finalize_match(winner=affair.winner, loser=affair.loser, reason=affair.reason)

    def _finalize_match(self, *, winner: Player, loser: Player, reason: str) -> None:
        """Mark the duel as over and record the declared winner."""
        self.state.game_over = True
        self.state.winner = winner

    def _register_forbid(self, affair: Forbid) -> None:
        self._forbids.append(affair)

    def _cleanup_forbids(self, affair: TurnCleanup) -> None:
        self._forbids = [f for f in self._forbids if f.outdated_when != affair]
        self.state.normal_summon_used = False

    def _advance_to_next_turn(self, affair: EnterPhase) -> None:
        self.state.current_player = self.state.opponent
        self.state.current_turn += 1
        affair.duel.dispatcher.emit(TurnCleanup(duel=affair.duel, turn=self.state.current_turn))
        self.state.phase = Phase.DRAW
        affair.duel.dispatcher.emit(
            EnterPhase(
                duel=affair.duel,
                phase=Phase.DRAW,
                source_phase=Phase.END,
                requester=self._advance_to_next_turn,
            )
        )

    def _expand_multi_affair(self, duel: Duel, affair: MultiAffair) -> None:
        for child in affair.children:
            self._apply_result(duel, child)

    def _apply_result(self, duel: Duel, affair: DuelAffair) -> None:
        match affair:
            case MultiAffair():
                self._expand_multi_affair(duel, affair)
            case TurnCleanup():
                duel.dispatcher.emit(affair)
            case Draw():
                self._apply_draw(affair)
            case EnterPhase():
                self._apply_enter_phase(affair)
            case NormalSummon():
                self._apply_normal_summon(affair)
            case SendToGraveyard():
                self._apply_send_to_graveyard(affair)
            case LpVary():
                self._apply_lp_vary(affair)
            case Forbid():
                self._register_forbid(affair)
            case _:
                raise ValueError(f"Unsupported result: {type(affair).__name__}")
