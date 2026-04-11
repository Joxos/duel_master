"""Kernel coordination surface for one duel instance.

This module owns the duel-bound execution coordinator. It creates the internal
dispatcher used for execution handlers and republishes completed affairs back to
the duel-level dispatcher.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from affairon import Dispatcher
from affairon.composer import PluginComposer
from pathlib import Path

from duel_core.affairs import (
    DuelAffairWithRequester,
    CompletedAffair,
    DuelAffair,
    ExposedUserAction,
    Forbid,
)
from duel_core.models import DuelState

PYPROJECT_PATH = Path(__file__).resolve().parents[3] / "pyproject.toml"

if TYPE_CHECKING:
    from affairon import Dispatcher as AffairDispatcher


class Kernel:
    """Kernel-owned execution coordinator for one duel.

    Attributes:
        state: Runtime duel state owned by the kernel.
        dispatcher: Internal dispatcher for execution listeners.
    """

    def __init__(self, state: DuelState, duel_dispatcher: AffairDispatcher) -> None:
        self.state = state
        self._forbids: list[Forbid] = []
        self.duel_dispatcher = duel_dispatcher
        self.dispatcher = Dispatcher()

        kernel_composer = PluginComposer(self.dispatcher)
        kernel_composer.compose_from_pyproject(PYPROJECT_PATH, profile="kernel")

    def is_forbidden(self, affair: DuelAffairWithRequester) -> bool:
        """Check whether an actionable affair is currently forbidden.

        Args:
            affair: The actionable affair to test.

        Returns:
            True when a matching forbid remains active in the current turn.
        """
        return any(
            forbid.target == affair and self.state.current_turn_count < forbid.inactive_from_turn
            for forbid in self._forbids
        )

    def do(self, action: ExposedUserAction) -> None:
        if self.is_forbidden(action):
            raise ValueError(f"Forbidden: {type(action).__name__}")
        self.dispatcher.emit(action)

    def complete(self, affair: DuelAffair) -> None:
        self.duel_dispatcher.emit(CompletedAffair(duel=affair.duel, affair=affair))
