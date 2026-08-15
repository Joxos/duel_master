from affairon import listen

from duel_core.mr2020.card.affairs import MoveCard
from duel_core.mr2020.card.models import REPRESENTATION
from duel_core.mr2020.duel.affairs import AvailableActions, CompletedAffair, DuelInit, MultiAction
from duel_core.mr2020.phase.models import Phase
from duel_core.mr2020.phase.runtime import PhaseRuntime
from duel_core.mr2020.player.runtime import PlayerRuntime
from duel_core.mr2020.summon.affairs import NormalSummon
from duel_core.mr2020.summon.runtime import SummonRuntime
from duel_core.mr2020.timing.affairs import AtomicAction
from duel_core.mr2020.timing.predicates import completed_affair_of
from duel_core.mr2020.turn.affairs import AdvanceTurn


@listen(DuelInit)
def setup_summon_runtime(affair: DuelInit) -> None:
    affair.duel.provide(SummonRuntime(normal_summon_used=False))


@listen(CompletedAffair, when=completed_affair_of(AdvanceTurn))
def reset_normal_summon_state(completed: CompletedAffair) -> None:
    completed.affair.duel.inject(SummonRuntime).set_normal_summon_used(False)


@listen(AvailableActions)
def offer_normal_summons(affair: AvailableActions) -> None:
    duel = affair.duel
    if duel.inject(PhaseRuntime).phase not in (Phase.MAIN_1, Phase.MAIN_2):
        return
    if duel.inject(SummonRuntime).normal_summon_used:
        return

    player_runtime = duel.inject(PlayerRuntime)
    current_player = player_runtime.current_player
    empty_zone = next((zone for zone in current_player.monster_zones if zone.card is None), None)
    if empty_zone is None:
        return

    for card in current_player.hand:
        if card.card.level is None or card.card.level > 4:
            continue
        affair.actions.append(
            NormalSummon(
                duel=duel,
                player=current_player,
                card=card,
                to_zone=empty_zone,
                from_representation=card.representation,
                to_representation=REPRESENTATION.ATTACK,
                requester=offer_normal_summons,
            )
        )


@listen(NormalSummon)
def apply_normal_summon(affair: NormalSummon) -> None:
    children: list[AtomicAction] = [
        MoveCard(
            duel=affair.duel,
            player=affair.player,
            card=affair.card,
            from_area="hand",
            to_area="monster_zone",
            to_zone=affair.to_zone,
            from_representation=affair.from_representation,
            to_representation=affair.to_representation,
        )
    ]
    affair.duel.emit(
        MultiAction(
            duel=affair.duel,
            requester=affair.requester,
            origin=affair,
            children=children,
        )
    )
    affair.duel.inject(SummonRuntime).set_normal_summon_used(True)
