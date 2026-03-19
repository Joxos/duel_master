"""Execution kernel for the current duel slice.

This module owns runtime state mutation, guarded execution, and the execution
loop that emits completion back into the affair graph.
"""

from affairon import Dispatcher

from duel_core.affairs import (
    ActionableDuelAffair,
    CompletedAffair,
    Draw,
    DuelAffair,
    EnterPhase,
    ExecutionRequest,
    Forbid,
    MultiAffair,
    NormalSummon,
    TurnCleanup,
)
from duel_core.models import DuelState
from duel_core.phase import Phase


class Kernel:
    """Runtime execution owner for the current duel slice.

    Attributes:
        state: Kernel-owned runtime duel state.
        supported_actions: Guarded affairs executable by the kernel.
    """

    def __init__(self, state: DuelState) -> None:
        self.state = state
        self._forbids: list[Forbid] = []
        self.supported_actions = (Draw, EnterPhase, NormalSummon, Forbid)

    def register(self, dispatcher: Dispatcher) -> None:
        dispatcher.on(ExecutionRequest)(self._execute_request)
        for action in self.supported_actions:
            dispatcher.on(action)(self._guarded_apply)
        dispatcher.on(TurnCleanup)(self._cleanup_forbids)

    def is_forbidden(self, affair: ActionableDuelAffair) -> bool:
        return any(
            forbid.target == affair and forbid.outdated_when.turn >= self.state.current_turn
            for forbid in self._forbids
        )

    def _execute_request(self, affair: ExecutionRequest) -> None:
        self._execute_affair(affair.duel, affair.affair)
        affair.duel.emit(CompletedAffair(duel=affair.duel, affair=affair.affair))

    def _apply_draw(self, affair: Draw) -> None:
        affair.player.hand.extend(affair.player.main_deck.draw(affair.num))

    def _apply_enter_phase(self, affair: EnterPhase) -> None:
        if affair.phase is Phase.END:
            self._advance_to_next_turn(affair)
            return
        self.state.phase = affair.phase

    def _apply_normal_summon(self, affair: NormalSummon) -> None:
        if self.state.normal_summon_used:
            raise ValueError("Normal summon already used this turn")

        empty_index = affair.player.monster_zones.index(None)
        hand_index = affair.player.hand.index(affair.card)

        affair.player.monster_zones[empty_index] = affair.player.hand.pop(hand_index)
        self.state.normal_summon_used = True

    def _raise_if_forbidden(self, affair: ActionableDuelAffair) -> None:
        if self.is_forbidden(affair):
            raise ValueError(f"Affair is forbidden for requester: {affair.requester.__name__}")

    def _guarded_apply(self, affair: DuelAffair) -> None:
        if isinstance(affair, ActionableDuelAffair):
            self._raise_if_forbidden(affair)
        match affair:
            case Draw():
                self._apply_draw(affair)
            case EnterPhase():
                self._apply_enter_phase(affair)
            case NormalSummon():
                self._apply_normal_summon(affair)
            case Forbid():
                self._register_forbid(affair)
            case _:
                raise ValueError(f"Unsupported guarded affair: {type(affair).__name__}")

    def _register_forbid(self, affair: Forbid) -> None:
        self._forbids.append(affair)

    def _cleanup_forbids(self, affair: TurnCleanup) -> None:
        self._forbids = [forbid for forbid in self._forbids if forbid.outdated_when != affair]
        self.state.normal_summon_used = False

    def _advance_to_next_turn(self, affair: EnterPhase) -> None:
        self.state.current_player = self.state.opponent
        self.state.current_turn += 1
        affair.duel.emit(TurnCleanup(duel=affair.duel, turn=self.state.current_turn))
        self.state.phase = Phase.DRAW
        affair.duel.emit(
            EnterPhase(
                duel=affair.duel,
                phase=Phase.DRAW,
                source_phase=Phase.END,
                requester=self._advance_to_next_turn,
            )
        )

    def _expand_multi_affair(self, affair: MultiAffair) -> None:
        for child in affair.children:
            self._execute_affair(affair.duel, child)

    def _execute_affair(self, duel, affair: DuelAffair) -> None:
        if isinstance(affair, MultiAffair):
            self._expand_multi_affair(affair)
            return

        duel.emit(affair)
