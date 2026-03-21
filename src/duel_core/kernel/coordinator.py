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
    NormalSummon,
    TurnCleanup,
)
from duel_core.kernel.appliers import DEFAULT_APPLIERS, ActionableApplier
from duel_core.kernel.planners import DEFAULT_PLANNERS, ActionPlanner
from duel_core.models import DuelState
from duel_core.phase import Phase

if TYPE_CHECKING:
    from duel_core.duel import Duel


class Kernel:
    def __init__(self, state: DuelState) -> None:
        self.state = state
        self._forbids: list[Forbid] = []
        self.dispatcher = Dispatcher()
        self._planners: tuple[ActionPlanner, ...] = DEFAULT_PLANNERS
        self._appliers: tuple[ActionableApplier, ...] = DEFAULT_APPLIERS

    def register(self, duel_dispatcher: Dispatcher) -> None:
        duel_dispatcher.on(ExecutionRequest)(self._execute_request)
        duel_dispatcher.on(Draw)(self._execute_top_level)
        duel_dispatcher.on(EnterPhase)(self._execute_top_level)
        duel_dispatcher.on(NormalSummon)(self._execute_top_level)
        duel_dispatcher.on(Attack)(self._execute_top_level)
        duel_dispatcher.on(Forbid)(self.register_forbid)
        duel_dispatcher.on(TurnCleanup)(self._cleanup_forbids)

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
        result = self.plan_result(action)
        self.apply_result(duel, result)
        duel.dispatcher.emit(CompletedAffair(duel=duel, action=action, result=result))

    def plan_result(self, affair: ExecutableAffair) -> DuelAffair:
        for planner in self._planners:
            if planner.supports(affair):
                return planner.plan(self.state, affair)
        raise ValueError(f"Unsupported executable: {type(affair).__name__}")

    def register_forbid(self, affair: Forbid) -> None:
        self._forbids.append(affair)

    def _cleanup_forbids(self, affair: TurnCleanup) -> None:
        self._forbids = [f for f in self._forbids if f.outdated_when != affair]
        self.state.normal_summon_used = False

    def advance_to_next_turn(self, affair: EnterPhase) -> None:
        self.state.current_player = self.state.opponent
        self.state.current_turn += 1
        affair.duel.dispatcher.emit(TurnCleanup(duel=affair.duel, turn=self.state.current_turn))
        self.state.phase = Phase.DRAW
        affair.duel.dispatcher.emit(
            EnterPhase(
                duel=affair.duel,
                phase=Phase.DRAW,
                source_phase=Phase.END,
                requester=self.advance_to_next_turn,
            )
        )

    def apply_result(self, duel: Duel, affair: DuelAffair) -> None:
        for applier in self._appliers:
            if applier.supports(affair):
                applier.apply(self, duel, affair)
                return
        raise ValueError(f"Unsupported result: {type(affair).__name__}")
