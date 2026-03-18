from affairon import Dispatcher
from duel_core.affairs import (
    AvailableActions,
    Draw,
    DuelInit,
    EnterPhase,
    Forbid,
    TurnCleanup,
)
from duel_core.phase import Phase

TURN_DRAW_NUM = 1
INITIAL_DRAW_NUM = 5

PHASE_GRAPH: dict[Phase, tuple[Phase, ...]] = {
    Phase.DRAW: (Phase.STANDBY,),
    Phase.STANDBY: (Phase.MAIN_1,),
    Phase.MAIN_1: (Phase.BATTLE, Phase.END),
    Phase.BATTLE: (Phase.MAIN_2,),
    Phase.MAIN_2: (Phase.END,),
}


def setup(dispatcher: Dispatcher) -> None:
    @dispatcher.on(EnterPhase)
    def turn_draw(affair: EnterPhase) -> None:
        if affair.phase is not Phase.DRAW:
            return

        affair.duel.emit(
            Draw(
                duel=affair.duel,
                player=affair.duel.state.current_player,
                num=TURN_DRAW_NUM,
                requester=turn_draw,
            )
        )

    @dispatcher.on(DuelInit)
    def initial_draw(affair: DuelInit) -> None:
        for player in affair.duel.state.players:
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
                outdated_when=TurnCleanup(
                    duel=affair.duel, turn=affair.duel.state.current_turn + 1
                ),
            )
        )

    @dispatcher.on(DuelInit)
    def forbid_first_turn_battle(affair: DuelInit) -> None:
        affair.duel.emit(
            Forbid(
                duel=affair.duel,
                target=phase_actions,
                outdated_when=TurnCleanup(
                    duel=affair.duel, turn=affair.duel.state.current_turn + 1
                ),
                source_phase=Phase.MAIN_1,
                target_phase=Phase.BATTLE,
            )
        )

    @dispatcher.on(AvailableActions)
    def phase_actions(affair: AvailableActions) -> None:
        for target_phase in PHASE_GRAPH.get(affair.duel.state.phase, ()):
            if affair.duel.kernel.is_phase_transition_forbidden(
                phase_actions,
                affair.duel.state.phase,
                target_phase,
            ):
                continue

            affair.actions.append(
                EnterPhase(
                    duel=affair.duel,
                    phase=target_phase,
                    source_phase=affair.duel.state.phase,
                    requester=phase_actions,
                )
            )
