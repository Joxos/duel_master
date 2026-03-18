from affairon import Dispatcher

from duel_core.affairs import (
    AvailableActions,
    Draw,
    DuelInit,
    EnterPhase,
    ExitPhase,
    Forbid,
    TurnCleanup,
)
from duel_core.phase import Phase

TURN_DRAW_NUM = 1
INITIAL_DRAW_NUM = 5


def setup(dispatcher: Dispatcher) -> None:
    @dispatcher.on(EnterPhase)
    def turn_draw(affair: EnterPhase) -> None:
        if affair.phase is not Phase.DRAW:
            return

        affair.duel.emit(
            Draw(
                duel=affair.duel,
                player=affair.duel.current_player,
                num=TURN_DRAW_NUM,
                requester=turn_draw,
            )
        )

    @dispatcher.on(DuelInit)
    def initial_draw(affair: DuelInit) -> None:
        for player in affair.duel.players:
            affair.duel.emit(
                Draw(
                    duel=affair.duel,
                    player=player,
                    num=INITIAL_DRAW_NUM,
                    requester=initial_draw,
                )
            )

    @dispatcher.on(DuelInit)
    def forbid_initial_turn_draw(affair: DuelInit) -> None:
        affair.duel.emit(
            Forbid(
                duel=affair.duel,
                target=turn_draw,
                outdated_when=TurnCleanup(duel=affair.duel, turn=affair.duel.current_turn + 1),
            )
        )

    @dispatcher.on(AvailableActions)
    def end_turn_action(affair: AvailableActions) -> None:
        if affair.duel.phase is not Phase.DRAW:
            return
        affair.actions.append(
            ExitPhase(
                label="End turn",
                duel=affair.duel,
                phase=Phase.END,
                requester=end_turn_action,
            )
        )

    @dispatcher.on(AvailableActions)
    def enter_draw_phase_action(affair: AvailableActions) -> None:
        if affair.duel.phase is Phase.DRAW:
            return
        affair.actions.append(
            EnterPhase(
                label="Enter Draw Phase",
                duel=affair.duel,
                phase=Phase.DRAW,
                requester=enter_draw_phase_action,
            )
        )
