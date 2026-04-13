from affairon import listen

from duel_core.mr2020.duel.affairs import CompletedAffair, DuelInit
from duel_core.mr2020.phase.affairs import EnterPhase
from duel_core.mr2020.phase.models import Phase
from duel_core.mr2020.turn.affairs import AdvanceTurn


@listen(DuelInit)
def inject_turn_count(affair: DuelInit) -> None:
    affair.duel._current_turn_count = 1


@listen(DuelInit, after=[inject_turn_count])
def inject_turn_helpers(affair: DuelInit) -> None:
    duel = affair.duel

    def get_current_turn_count() -> int:
        return duel._current_turn_count

    def set_current_turn_count(turn_count: int) -> None:
        duel._current_turn_count = turn_count

    duel.get_current_turn_count = get_current_turn_count
    duel.set_current_turn_count = set_current_turn_count


@listen(AdvanceTurn)
def apply_advance_turn(affair: AdvanceTurn) -> None:
    affair.duel.set_current_player(affair.to_player)
    affair.duel.set_current_turn_count(affair.to_turn)
    affair.duel.emit(CompletedAffair(duel=affair.duel, affair=affair))
    affair.duel.emit(
        EnterPhase(
            duel=affair.duel,
            phase=Phase.DRAW,
            source_phase=Phase.END,
            requester=apply_advance_turn,
        )
    )
