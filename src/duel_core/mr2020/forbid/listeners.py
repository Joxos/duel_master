from affairon import listen

from duel_core.mr2020.duel.affairs import CompletedAffair, DuelInit
from duel_core.mr2020.forbid.affairs import Forbid
from duel_core.mr2020.forbid.runtime import ForbidRuntime
from duel_core.mr2020.timing.predicates import completed_affair_of
from duel_core.mr2020.turn.affairs import AdvanceTurn


@listen(DuelInit)
def setup_forbid_runtime(affair: DuelInit) -> None:
    affair.duel.provide(ForbidRuntime(duel=affair.duel))


@listen(Forbid)
def remember_forbid(affair: Forbid) -> None:
    affair.duel.inject(ForbidRuntime).active_forbids.append(affair)


@listen(CompletedAffair, when=completed_affair_of(AdvanceTurn))
def expire_turn_forbids(completed: CompletedAffair) -> None:
    affair = completed.affair
    assert isinstance(affair, AdvanceTurn)
    runtime = affair.duel.inject(ForbidRuntime)
    runtime.active_forbids = [
        forbid for forbid in runtime.active_forbids if forbid.inactive_from_turn > affair.to_turn
    ]
