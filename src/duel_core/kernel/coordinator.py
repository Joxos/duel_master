from __future__ import annotations

from typing import TYPE_CHECKING

from affairon import Dispatcher

from duel_core.affairs import (
    ActionableDuelAffair,
    CompletedAffair,
    DuelAffair,
    ExecutableAffair,
    Forbid,
)
from duel_core.kernel.appliers import (
    DrawApplier,
    EnterPhaseApplier,
    ForbidBridge,
    LpVaryApplier,
    MultiAffairApplier,
    NormalSummonApplier,
    SendToGraveyardApplier,
    TurnCleanupBridge,
)
from duel_core.kernel.planners import AttackPlanner
from duel_core.models import DuelState

if TYPE_CHECKING:
    from affairon import Dispatcher as AffairDispatcher


class Kernel:
    def __init__(self, state: DuelState, duel_dispatcher: AffairDispatcher) -> None:
        self.state = state
        self._forbids: list[Forbid] = []
        self.duel_dispatcher = duel_dispatcher
        self.dispatcher = Dispatcher()

        AttackPlanner(kernel=self, dispatcher=self.dispatcher)
        MultiAffairApplier(kernel=self, dispatcher=self.dispatcher)
        DrawApplier(kernel=self, dispatcher=self.dispatcher)
        EnterPhaseApplier(kernel=self, dispatcher=self.dispatcher)
        NormalSummonApplier(kernel=self, dispatcher=self.dispatcher)
        SendToGraveyardApplier(kernel=self, dispatcher=self.dispatcher)
        LpVaryApplier(kernel=self, dispatcher=self.dispatcher)

        ForbidBridge(kernel=self, dispatcher=self.duel_dispatcher)
        TurnCleanupBridge(kernel=self, dispatcher=self.duel_dispatcher)

    def is_forbidden(self, affair: ActionableDuelAffair) -> bool:
        return any(
            forbid.target == affair and forbid.outdated_when.turn >= self.state.current_turn
            for forbid in self._forbids
        )

    def do(self, action: ExecutableAffair) -> None:
        if self.is_forbidden(action):
            raise ValueError(f"Forbidden: {type(action).__name__}")
        self.dispatcher.emit(action)

    def complete(self, affair: DuelAffair) -> None:
        self.duel_dispatcher.emit(CompletedAffair(duel=affair.duel, affair=affair))
