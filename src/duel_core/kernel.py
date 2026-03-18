from collections.abc import Callable

from affairon import Dispatcher

from duel_core.affairs import (
    CompletedAffair,
    Draw,
    DuelAffair,
    EnterPhase,
    ExecutionRequest,
    ExitPhase,
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
        dispatcher.on(ExitPhase)(self._handle_exit_phase)

    def is_forbidden(self, target: Callable[..., object]) -> bool:
        return any(
            forbid.target is target and forbid.outdated_when.turn >= self.state.current_turn
            for forbid in self._forbids
        )

    def _execute_request(self, affair: ExecutionRequest) -> None:
        self._execute_affair(affair.duel, affair.affair)
        affair.duel.emit(CompletedAffair(duel=affair.duel, affair=affair.affair))

    def _apply_draw(self, affair: Draw) -> None:
        if self.is_forbidden(affair.requester):
            raise ValueError(f"Affair is forbidden for requester: {affair.requester.__name__}")
        affair.player.hand.extend(affair.player.main_deck.draw(affair.num))

    def _register_forbid(self, affair: Forbid) -> None:
        self._forbids.append(affair)

    def _cleanup_forbids(self, affair: TurnCleanup) -> None:
        self._forbids = [forbid for forbid in self._forbids if forbid.outdated_when != affair]

    def _handle_exit_phase(self, affair: ExitPhase) -> None:
        if affair.phase is not Phase.END:
            return
        current_index = self.state.players.index(self.state.current_player)
        self.state.current_player = self.state.players[
            (current_index + 1) % len(self.state.players)
        ]
        self.state.current_turn += 1
        affair.duel.emit(TurnCleanup(duel=affair.duel, turn=self.state.current_turn))
        self.state.phase = Phase.DRAW
        affair.duel.emit(
            EnterPhase(duel=affair.duel, phase=Phase.DRAW, requester=self._handle_exit_phase)
        )

    def _execute_affair(self, duel, affair: DuelAffair) -> None:
        if isinstance(affair, MultiAffair):
            for child in affair.children:
                self._execute_affair(duel, child)
            return

        duel.emit(affair)
