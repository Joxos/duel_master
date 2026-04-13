from __future__ import annotations

from affairon import MutableAffair
from pydantic import ConfigDict


class ExposedUserAction(MutableAffair):
    label: str | None = None

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        strict=True,
        arbitrary_types_allowed=True,
    )


class TimingAction(ExposedUserAction):
    pass


class AtomicAction(MutableAffair):
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        strict=True,
        arbitrary_types_allowed=True,
    )


def rebuild_timing_models(namespace: dict[str, object]) -> None:
    for model in (AtomicAction, ExposedUserAction, TimingAction):
        model.model_rebuild(_types_namespace=namespace)
