from __future__ import annotations

from typing import TYPE_CHECKING

from duel_core.mr2020.duel.affairs import DuelAffairWithRequester

if TYPE_CHECKING:
    from duel_core.mr2020.duel.models import Duel


def is_forbidden(duel: Duel, affair: DuelAffairWithRequester) -> bool:
    return any(
        forbid.target == affair and duel.get_current_turn_count() < forbid.inactive_from_turn
        for forbid in duel.get_active_forbids()
    )
