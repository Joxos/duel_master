from __future__ import annotations

from typing import TYPE_CHECKING

from affairon import AffairAware
from affairon.listen import listen

from duel_core.affairs import (
    Draw,
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
    pass


class MultiAffairApplier(AffairAware):
    def __init__(self, kernel):
        self.kernel = kernel

    @listen(MultiAffair)
    def on_multi_affair(self, affair: MultiAffair) -> None:
        for child in affair.children:
            self.kernel.dispatcher.emit(child)
        self.kernel.complete(affair)


class DrawApplier(AffairAware):
    def __init__(self, kernel):
        self.kernel = kernel

    @listen(Draw)
    def on_draw(self, affair: Draw) -> None:
        drawn = affair.player.main_deck.draw(affair.num)
        affair.player.hand.extend(RuntimeCard(card=c) for c in drawn)
        self.kernel.complete(affair)


class EnterPhaseApplier(AffairAware):
    def __init__(self, kernel):
        self.kernel = kernel

    @listen(EnterPhase)
    def on_enter_phase(self, affair: EnterPhase) -> None:
        if affair.phase is Phase.END:
            self.kernel.state.phase = affair.phase
            self.kernel.complete(affair)
            self.kernel.state.current_player = self.kernel.state.opponent
            self.kernel.state.current_turn += 1
            self.kernel.duel_dispatcher.emit(
                TurnCleanup(duel=affair.duel, turn=self.kernel.state.current_turn)
            )
            self.kernel.do(
                EnterPhase(
                    duel=affair.duel,
                    phase=Phase.DRAW,
                    source_phase=affair.phase,
                    requester=self.on_enter_phase,
                )
            )
            return
        self.kernel.state.phase = affair.phase
        self.kernel.complete(affair)


class NormalSummonApplier(AffairAware):
    def __init__(self, kernel):
        self.kernel = kernel

    @listen(NormalSummon)
    def on_normal_summon(self, affair: NormalSummon) -> None:
        if self.kernel.state.normal_summon_used:
            raise ValueError("Normal summon already used this turn")
        empty_zone = affair.player.monster_zones.index(None)
        hand_index = affair.player.hand.index(affair.card)
        affair.player.monster_zones[empty_zone] = affair.player.hand.pop(hand_index)
        affair.card.representation = REPRESENTATION.ATTACK
        self.kernel.state.normal_summon_used = True
        self.kernel.complete(affair)


class SendToGraveyardApplier(AffairAware):
    def __init__(self, kernel):
        self.kernel = kernel

    @listen(SendToGraveyard)
    def on_send_to_graveyard(self, affair: SendToGraveyard) -> None:
        zone_index = affair.player.monster_zones.index(affair.card)
        affair.player.monster_zones[zone_index] = None
        affair.card.representation = REPRESENTATION.VOID
        affair.player.graveyard.append(affair.card)


class LpVaryApplier(AffairAware):
    def __init__(self, kernel):
        self.kernel = kernel

    @listen(LpVary)
    def on_lp_vary(self, affair: LpVary) -> None:
        affair.player.life_points += affair.delta


class ForbidBridge(AffairAware):
    def __init__(self, kernel):
        self.kernel = kernel

    @listen(Forbid)
    def on_forbid(self, affair: Forbid) -> None:
        self.kernel._forbids.append(affair)


class TurnCleanupBridge(AffairAware):
    def __init__(self, kernel):
        self.kernel = kernel

    @listen(TurnCleanup)
    def on_turn_cleanup(self, affair: TurnCleanup) -> None:
        self.kernel._forbids = [f for f in self.kernel._forbids if f.outdated_when != affair]
        self.kernel.state.normal_summon_used = False
