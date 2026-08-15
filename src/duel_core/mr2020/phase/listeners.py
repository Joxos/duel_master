from __future__ import annotations

from affairon import listen

from duel_core.mr2020.duel.affairs import AvailableActions, CompletedAffair, DuelInit
from duel_core.mr2020.phase.affairs import EnterPhase
from duel_core.mr2020.phase.models import Phase
from duel_core.mr2020.phase.runtime import PhaseRuntime
from duel_core.mr2020.player.runtime import PlayerRuntime
from duel_core.mr2020.turn.runtime import TurnRuntime
from duel_core.mr2020.turn.affairs import AdvanceTurn

PHASE_GRAPH: dict[Phase, tuple[Phase, ...]] = {
    Phase.DRAW: (Phase.STANDBY,),
    Phase.STANDBY: (Phase.MAIN_1,),
    Phase.MAIN_1: (Phase.BATTLE, Phase.END),
    Phase.BATTLE: (Phase.MAIN_2,),
    Phase.MAIN_2: (Phase.END,),
}


@listen(DuelInit)
def setup_phase_runtime(affair: DuelInit) -> None:
    affair.duel.provide(PhaseRuntime(phase=Phase.DRAW))


@listen(AvailableActions)
def offer_phase_actions(affair: AvailableActions) -> None:
    from duel_core.mr2020.forbid.policy import is_forbidden

    phase = affair.duel.inject(PhaseRuntime).phase
    for target_phase in PHASE_GRAPH.get(phase, ()):
        action = EnterPhase(
            duel=affair.duel,
            phase=target_phase,
            source_phase=phase,
            requester=offer_phase_actions,
        )
        if is_forbidden(affair.duel, action):
            continue
        affair.actions.append(action)


@listen(EnterPhase, when=lambda affair: affair.phase is not Phase.END)
def apply_phase_entry(affair: EnterPhase) -> None:
    affair.duel.inject(PhaseRuntime).set_phase(affair.phase)
    affair.duel.emit(CompletedAffair(duel=affair.duel, affair=affair))


@listen(EnterPhase, when=lambda affair: affair.phase is Phase.END)
def complete_end_phase(affair: EnterPhase) -> None:
    duel = affair.duel
    duel.inject(PhaseRuntime).set_phase(affair.phase)
    affair.duel.emit(CompletedAffair(duel=affair.duel, affair=affair))
    turn_runtime = duel.inject(TurnRuntime)
    player_runtime = duel.inject(PlayerRuntime)
    affair.duel.emit(
        AdvanceTurn(
            duel=duel,
            from_turn=turn_runtime.current_turn_count,
            to_turn=turn_runtime.current_turn_count + 1,
            from_player=player_runtime.current_player,
            to_player=player_runtime.opponent_of(player_runtime.current_player),
        )
    )
