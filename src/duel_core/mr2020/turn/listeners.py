from affairon import listen

from duel_core.mr2020.duel.affairs import CompletedAffair, DuelInit
from duel_core.mr2020.phase.affairs import EnterPhase
from duel_core.mr2020.phase.models import Phase
from duel_core.mr2020.player.runtime import PlayerRuntime
from duel_core.mr2020.turn.runtime import TurnRuntime
from duel_core.mr2020.turn.affairs import AdvanceTurn


@listen(DuelInit)
def setup_turn_runtime(affair: DuelInit) -> None:
    affair.duel.provide(TurnRuntime(current_turn_count=1))


@listen(AdvanceTurn)
def apply_advance_turn(affair: AdvanceTurn) -> None:
    affair.duel.inject(PlayerRuntime).set_current_player(affair.to_player)
    affair.duel.inject(TurnRuntime).set_current_turn_count(affair.to_turn)
    affair.duel.emit(CompletedAffair(duel=affair.duel, affair=affair))
    affair.duel.emit(
        EnterPhase(
            duel=affair.duel,
            phase=Phase.DRAW,
            source_phase=Phase.END,
            requester=apply_advance_turn,
        )
    )
