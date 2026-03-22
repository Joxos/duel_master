"""Duel-dispatcher bridge listeners for kernel-owned bookkeeping.

This module contains listeners that stay on the duel dispatcher while updating
kernel-owned bookkeeping state such as active forbids and turn cleanup.
"""

from affairon.listen import listen

from duel_core.affairs import Forbid, TurnCleanup


@listen(Forbid)
def on_forbid(affair: Forbid) -> None:
    affair.duel.kernel._forbids.append(affair)


@listen(TurnCleanup)
def on_turn_cleanup(affair: TurnCleanup) -> None:
    kernel = affair.duel.kernel
    kernel._forbids = [f for f in kernel._forbids if f.outdated_when != affair]
    kernel.state.normal_summon_used = False
