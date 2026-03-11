from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TypedDict


class ChoiceRequest(TypedDict, total=False):
    type: str
    options: Sequence[object]


Choice = object | None


class Policy(ABC):
    @abstractmethod
    def choose(
        self,
        state: object,
        choice_request: ChoiceRequest,
    ) -> Choice:
        raise NotImplementedError
