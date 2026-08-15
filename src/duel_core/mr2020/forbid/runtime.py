from __future__ import annotations

from typing import TYPE_CHECKING

from duel_core.mr2020.duel.affairs import DuelAffairWithRequester
from duel_core.mr2020.forbid.affairs import Forbid

if TYPE_CHECKING:
    from duel_core.mr2020.duel.models import Duel


class ForbidRuntime:
    def __init__(self, duel: Duel) -> None:
        self.duel = duel
        self.active_forbids: list[Forbid] = []

    def do(self, action: DuelAffairWithRequester) -> None:
        from duel_core.mr2020.forbid.policy import is_forbidden

        if is_forbidden(self.duel, action):
            raise ValueError(f"Forbidden: {type(action).__name__}")
        self.duel.emit(action)
