from __future__ import annotations

from affairon import listen

from duel_core.mr2020.duel.affairs import AvailableActions, CompletedAffair, DuelInit
from duel_core.mr2020.phase.affairs import EnterPhase
from duel_core.mr2020.phase.models import Phase
from duel_core.mr2020.turn.affairs import AdvanceTurn

PHASE_GRAPH: dict[Phase, tuple[Phase, ...]] = {
    Phase.DRAW: (Phase.STANDBY,),
    Phase.STANDBY: (Phase.MAIN_1,),
    Phase.MAIN_1: (Phase.BATTLE, Phase.END),
    Phase.BATTLE: (Phase.MAIN_2,),
    Phase.MAIN_2: (Phase.END,),
}


@listen(DuelInit)
def inject_current_phase(affair: DuelInit) -> None:
    affair.duel._phase = Phase.DRAW


@listen(DuelInit, after=[inject_current_phase])
def inject_phase_helpers(affair: DuelInit) -> None:
    duel = affair.duel

    def get_phase() -> Phase:
        return duel._phase

    def set_phase(phase: Phase) -> None:
        duel._phase = phase

    duel.get_phase = get_phase
    duel.set_phase = set_phase


@listen(AvailableActions)
def offer_phase_actions(affair: AvailableActions) -> None:
    from duel_core.mr2020.forbid.policy import is_forbidden

    for target_phase in PHASE_GRAPH.get(affair.duel.get_phase(), ()):
        action = EnterPhase(
            duel=affair.duel,
            phase=target_phase,
            source_phase=affair.duel.get_phase(),
            requester=offer_phase_actions,
        )
        if is_forbidden(affair.duel, action):
            continue
        affair.actions.append(action)


@listen(EnterPhase, when=lambda affair: affair.phase is not Phase.END)
def apply_phase_entry(affair: EnterPhase) -> None:
    affair.duel.set_phase(affair.phase)
    affair.duel.emit(CompletedAffair(duel=affair.duel, affair=affair))


@listen(EnterPhase, when=lambda affair: affair.phase is Phase.END)
def complete_end_phase(affair: EnterPhase) -> None:
    affair.duel.set_phase(affair.phase)
    affair.duel.emit(CompletedAffair(duel=affair.duel, affair=affair))
    affair.duel.emit(
        AdvanceTurn(
            duel=affair.duel,
            from_turn=affair.duel.get_current_turn_count(),
            to_turn=affair.duel.get_current_turn_count() + 1,
            from_player=affair.duel.get_current_player(),
            to_player=affair.duel.opponent_of(affair.duel.get_current_player()),
        )
    )
