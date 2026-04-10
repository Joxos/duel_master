"""Duel-dispatcher bridge listeners for kernel-owned bookkeeping.

This module contains listeners that stay on the duel dispatcher while updating
kernel-owned bookkeeping state such as active forbids and their expiry.
"""

from affairon.listen import listen

from duel_core.affairs import AdvanceTurn, CompletedAffair, Forbid, completed_affair_of


@listen(Forbid)
def on_forbid(affair: Forbid) -> None:
    affair.duel.kernel._forbids.append(affair)


@listen(CompletedAffair, when=completed_affair_of(AdvanceTurn))
def expire_turn_forbids(completed: CompletedAffair) -> None:
    affair = completed.affair
    assert isinstance(affair, AdvanceTurn)
    affair.duel.kernel._forbids = [
        forbid
        for forbid in affair.duel.kernel._forbids
        if forbid.inactive_from_turn > affair.to_turn
    ]
