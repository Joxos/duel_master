from __future__ import annotations

from typing import TYPE_CHECKING

from duel_core.mr2020.duel.affairs import DuelAffairWithRequester
from duel_core.mr2020.forbid.runtime import ForbidRuntime
from duel_core.mr2020.turn.runtime import TurnRuntime

if TYPE_CHECKING:
    from duel_core.mr2020.duel.models import Duel


def is_forbidden(duel: Duel, affair: DuelAffairWithRequester) -> bool:
    turn = duel.inject(TurnRuntime).current_turn_count
    forbids = duel.inject(ForbidRuntime).active_forbids
    return any(forbid.target == affair and turn < forbid.inactive_from_turn for forbid in forbids)
