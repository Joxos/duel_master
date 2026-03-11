from __future__ import annotations

from typing import override

from .base import ChoiceRequest, Policy


class StrictManualPolicy(Policy):
    @override
    def choose(
        self,
        state: object,
        choice_request: ChoiceRequest,
    ) -> None:
        return None
