from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from affairon import MutableAffair
from pydantic import ConfigDict, Field

if TYPE_CHECKING:
    from duel_core.mr2020.duel.models import Duel
    from duel_core.mr2020.timing.affairs import AtomicAction


class DuelAffair(MutableAffair):
    duel: Duel

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        strict=True,
        arbitrary_types_allowed=True,
    )


class DuelAffairWithRequester(DuelAffair):
    requester: Callable[..., object]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DuelAffairWithRequester):
            return False
        return self.requester is other.requester


class AvailableActions(DuelAffair):
    actions: list[DuelAffairWithRequester] = Field(default_factory=list)


class CompletedAffair(DuelAffair):
    affair: DuelAffair


class MultiAction(DuelAffairWithRequester):
    origin: DuelAffair
    children: list[AtomicAction] = Field(default_factory=list)


class DuelInit(DuelAffair):
    pass


def rebuild_duel_models(namespace: dict[str, object]) -> None:
    for model in (
        AvailableActions,
        CompletedAffair,
        DuelAffair,
        DuelAffairWithRequester,
        DuelInit,
        MultiAction,
    ):
        model.model_rebuild(_types_namespace=namespace)


__all__ = [
    "AvailableActions",
    "CompletedAffair",
    "DuelAffair",
    "DuelAffairWithRequester",
    "DuelInit",
    "MultiAction",
    "rebuild_duel_models",
]
