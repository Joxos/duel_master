from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from affairon import MutableAffair
from pydantic import ConfigDict

if TYPE_CHECKING:
    from duel_core.duel import Duel


class DuelAffair(MutableAffair):
    """Base affair carrying duel context through the runtime graph.

    Attributes:
        duel: Duel instance that owns the current execution graph.
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        strict=True,
        arbitrary_types_allowed=True,
    )

    duel: Duel


class AtomicAction(DuelAffair):
    pass


class DuelAffairWithRequester(DuelAffair):
    """Affair whose semantic source matters for identity checks.

    Attributes:
        requester: Callable that contributed or requested this affair.
    """

    requester: Callable[..., object]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DuelAffairWithRequester):
            return False
        return self.requester is other.requester


class ExposedUserAction(DuelAffairWithRequester):
    """Affair that can be surfaced to the user as an executable action.

    Attributes:
        label: Optional presentation label for UI surfaces.
    """

    label: str | None = None
