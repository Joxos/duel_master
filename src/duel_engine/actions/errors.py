from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ActionError(Exception):
    message: str

    def __str__(self) -> str:
        return self.message


class InvalidActionError(ActionError):
    pass


class InvalidPhaseError(ActionError):
    pass


class IllegalTargetError(ActionError):
    pass


class InsufficientResourcesError(ActionError):
    pass


class WrongPlayerError(ActionError):
    pass
