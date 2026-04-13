from affairon import listen

from duel_core.mr2020.duel.affairs import CompletedAffair, DuelAffairWithRequester, DuelInit
from duel_core.mr2020.forbid.affairs import Forbid
from duel_core.mr2020.forbid.policy import is_forbidden
from duel_core.mr2020.timing.predicates import completed_affair_of
from duel_core.mr2020.turn.affairs import AdvanceTurn


@listen(DuelInit)
def inject_active_forbids(affair: DuelInit) -> None:
    affair.duel._active_forbids = []


@listen(DuelInit, after=[inject_active_forbids])
def inject_forbid_helpers(affair: DuelInit) -> None:
    duel = affair.duel

    def get_active_forbids() -> list[Forbid]:
        return duel._active_forbids

    def do(action: DuelAffairWithRequester) -> None:
        if is_forbidden(duel, action):
            raise ValueError(f"Forbidden: {type(action).__name__}")
        duel.emit(action)

    duel.get_active_forbids = get_active_forbids
    duel.do = do


@listen(Forbid)
def remember_forbid(affair: Forbid) -> None:
    affair.duel._active_forbids.append(affair)


@listen(CompletedAffair, when=completed_affair_of(AdvanceTurn))
def expire_turn_forbids(completed: CompletedAffair) -> None:
    affair = completed.affair
    assert isinstance(affair, AdvanceTurn)
    affair.duel._active_forbids = [
        forbid
        for forbid in affair.duel._active_forbids
        if forbid.inactive_from_turn > affair.to_turn
    ]
