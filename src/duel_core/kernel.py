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
    TurnCleanup,
)
from duel_core.models import DuelState
from duel_core.phase import Phase


class Kernel:
    def __init__(self, state: DuelState) -> None:
        self.state = state
        self._forbids: list[Forbid] = []

    def register(self, dispatcher: Dispatcher) -> None:
        dispatcher.on(ExecutionRequest)(self._execute_request)
        dispatcher.on(Draw)(self._apply_draw)
        dispatcher.on(Forbid)(self._register_forbid)
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
        if self.is_forbidden(affair):
            raise ValueError(f"Affair is forbidden for requester: {affair.requester.__name__}")
        affair.player.hand.extend(affair.player.main_deck.draw(affair.num))

    def _apply_enter_phase(self, affair: EnterPhase) -> None:
        if self.is_forbidden(affair):
            raise ValueError(f"Affair is forbidden for requester: {affair.requester.__name__}")
        if affair.phase is Phase.END:
            self._advance_to_next_turn(affair)
            return
        self.state.phase = affair.phase

    def _register_forbid(self, affair: Forbid) -> None:
        self._forbids.append(affair)

    def _cleanup_forbids(self, affair: TurnCleanup) -> None:
        self._forbids = [forbid for forbid in self._forbids if forbid.outdated_when != affair]

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

        if isinstance(affair, EnterPhase):
            self._apply_enter_phase(affair)

        duel.emit(affair)
