from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import override

from .base import Choice, ChoiceRequest, Policy


@dataclass(slots=True)
class DeterministicDefaultPolicy(Policy):
    choice_log: list[dict[str, Choice]] = field(default_factory=list)

    @override
    def choose(
        self,
        state: object,
        choice_request: ChoiceRequest,
    ) -> Choice:
        request_type = str(choice_request.get("type", ""))
        options = choice_request.get("options")
        choice = self._default_choice(request_type=request_type, options=options)
        self.choice_log.append(
            {
                "request_type": request_type,
                "choice": choice,
            }
        )
        return choice

    def _default_choice(
        self,
        *,
        request_type: str,
        options: object | None,
    ) -> Choice:
        if request_type == "pass_priority":
            return "pass"

        if isinstance(options, Sequence) and not isinstance(
            options, str | bytes | bytearray
        ):
            normalized_options = list(options)
        else:
            normalized_options = []

        if request_type == "choose_targets":
            if not normalized_options:
                return []
            return [normalized_options[0]]

        if request_type == "resolve_chain":
            if not normalized_options:
                return None
            return normalized_options[0]

        if not normalized_options:
            return None
        return normalized_options[0]
