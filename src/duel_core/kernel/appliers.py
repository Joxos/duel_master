from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from duel_core.affairs import (
    Draw,
    DuelAffair,
    EnterPhase,
    Forbid,
    LpVary,
    MultiAffair,
    NormalSummon,
    SendToGraveyard,
    TurnCleanup,
)
from duel_core.models import RuntimeCard, REPRESENTATION
from duel_core.phase import Phase

if TYPE_CHECKING:
    from duel_core.duel import Duel
    from duel_core.kernel.coordinator import Kernel


class ActionableApplier(ABC):
    @abstractmethod
    def supports(self, affair: DuelAffair) -> bool: ...

    @abstractmethod
    def apply(self, kernel: Kernel, duel: Duel, affair: DuelAffair) -> None: ...


class MultiAffairApplier(ActionableApplier):
    def supports(self, affair: DuelAffair) -> bool:
        return isinstance(affair, MultiAffair)

    def apply(self, kernel: Kernel, duel: Duel, affair: DuelAffair) -> None:
        if not isinstance(affair, MultiAffair):
            raise ValueError(f"Unsupported result: {type(affair).__name__}")
        for child in affair.children:
            kernel.apply_result(duel, child)


class DrawApplier(ActionableApplier):
    def supports(self, affair: DuelAffair) -> bool:
        return isinstance(affair, Draw)

    def apply(self, kernel: Kernel, duel: Duel, affair: DuelAffair) -> None:
        del kernel, duel
        if not isinstance(affair, Draw):
            raise ValueError(f"Unsupported result: {type(affair).__name__}")
        drawn = affair.player.main_deck.cards[: affair.num]
        del affair.player.main_deck.cards[: affair.num]
        affair.player.hand.extend(RuntimeCard(card=c) for c in drawn)


class EnterPhaseApplier(ActionableApplier):
    def supports(self, affair: DuelAffair) -> bool:
        return isinstance(affair, EnterPhase)

    def apply(self, kernel: Kernel, duel: Duel, affair: DuelAffair) -> None:
        del duel
        if not isinstance(affair, EnterPhase):
            raise ValueError(f"Unsupported result: {type(affair).__name__}")
        if affair.phase is Phase.END:
            kernel.advance_to_next_turn(affair)
            return
        kernel.state.phase = affair.phase


class NormalSummonApplier(ActionableApplier):
    def supports(self, affair: DuelAffair) -> bool:
        return isinstance(affair, NormalSummon)

    def apply(self, kernel: Kernel, duel: Duel, affair: DuelAffair) -> None:
        del duel
        if not isinstance(affair, NormalSummon):
            raise ValueError(f"Unsupported result: {type(affair).__name__}")
        if kernel.state.normal_summon_used:
            raise ValueError("Normal summon already used this turn")
        empty_zone = affair.player.monster_zones.index(None)
        hand_index = affair.player.hand.index(affair.card)
        affair.player.monster_zones[empty_zone] = affair.player.hand.pop(hand_index)
        affair.card.representation = REPRESENTATION.ATTACK
        kernel.state.normal_summon_used = True


class SendToGraveyardApplier(ActionableApplier):
    def supports(self, affair: DuelAffair) -> bool:
        return isinstance(affair, SendToGraveyard)

    def apply(self, kernel: Kernel, duel: Duel, affair: DuelAffair) -> None:
        del kernel, duel
        if not isinstance(affair, SendToGraveyard):
            raise ValueError(f"Unsupported result: {type(affair).__name__}")
        zone_index = affair.player.monster_zones.index(affair.card)
        affair.player.monster_zones[zone_index] = None
        affair.card.representation = REPRESENTATION.VOID
        affair.player.graveyard.append(affair.card)


class LpVaryApplier(ActionableApplier):
    def supports(self, affair: DuelAffair) -> bool:
        return isinstance(affair, LpVary)

    def apply(self, kernel: Kernel, duel: Duel, affair: DuelAffair) -> None:
        del kernel, duel
        if not isinstance(affair, LpVary):
            raise ValueError(f"Unsupported result: {type(affair).__name__}")
        affair.player.life_points += affair.delta


class ForbidApplier(ActionableApplier):
    def supports(self, affair: DuelAffair) -> bool:
        return isinstance(affair, Forbid)

    def apply(self, kernel: Kernel, duel: Duel, affair: DuelAffair) -> None:
        del duel
        if not isinstance(affair, Forbid):
            raise ValueError(f"Unsupported result: {type(affair).__name__}")
        kernel.register_forbid(affair)


class TurnCleanupApplier(ActionableApplier):
    def supports(self, affair: DuelAffair) -> bool:
        return isinstance(affair, TurnCleanup)

    def apply(self, kernel: Kernel, duel: Duel, affair: DuelAffair) -> None:
        del kernel
        if not isinstance(affair, TurnCleanup):
            raise ValueError(f"Unsupported result: {type(affair).__name__}")
        duel.dispatcher.emit(affair)


DEFAULT_APPLIERS: tuple[ActionableApplier, ...] = (
    MultiAffairApplier(),
    TurnCleanupApplier(),
    DrawApplier(),
    EnterPhaseApplier(),
    NormalSummonApplier(),
    SendToGraveyardApplier(),
    LpVaryApplier(),
    ForbidApplier(),
)
