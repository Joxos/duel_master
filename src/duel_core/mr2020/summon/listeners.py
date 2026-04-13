from affairon import listen

from duel_core.mr2020.card.affairs import MoveCard
from duel_core.mr2020.card.models import REPRESENTATION
from duel_core.mr2020.card.listeners import apply_move_card
from duel_core.mr2020.duel.affairs import AvailableActions, CompletedAffair, DuelInit
from duel_core.mr2020.phase.models import Phase
from duel_core.mr2020.summon.affairs import NormalSummon
from duel_core.mr2020.timing.predicates import completed_affair_of
from duel_core.mr2020.turn.affairs import AdvanceTurn


@listen(DuelInit)
def inject_normal_summon_state(affair: DuelInit) -> None:
    affair.duel._normal_summon_used = False


@listen(DuelInit, after=[inject_normal_summon_state])
def inject_normal_summon_helpers(affair: DuelInit) -> None:
    duel = affair.duel

    def get_normal_summon_used() -> bool:
        return duel._normal_summon_used

    def set_normal_summon_used(used: bool) -> None:
        duel._normal_summon_used = used

    duel.get_normal_summon_used = get_normal_summon_used
    duel.set_normal_summon_used = set_normal_summon_used


@listen(CompletedAffair, when=completed_affair_of(AdvanceTurn))
def reset_normal_summon_state(completed: CompletedAffair) -> None:
    completed.affair.duel.set_normal_summon_used(False)


@listen(AvailableActions)
def offer_normal_summons(affair: AvailableActions) -> None:
    if affair.duel.get_phase() not in (Phase.MAIN_1, Phase.MAIN_2):
        return
    if affair.duel.get_normal_summon_used():
        return

    empty_zone = next(
        (zone for zone in affair.duel.get_current_player().monster_zones if zone.card is None), None
    )
    if empty_zone is None:
        return

    for card in affair.duel.get_current_player().hand:
        if card.card.level is None or card.card.level > 4:
            continue
        affair.actions.append(
            NormalSummon(
                duel=affair.duel,
                player=affair.duel.get_current_player(),
                card=card,
                to_zone=empty_zone,
                from_representation=card.representation,
                to_representation=REPRESENTATION.ATTACK,
                requester=offer_normal_summons,
            )
        )


@listen(NormalSummon)
def apply_normal_summon(affair: NormalSummon) -> None:
    apply_move_card(
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
    )
    affair.duel.set_normal_summon_used(True)
    affair.duel.emit(CompletedAffair(duel=affair.duel, affair=affair))
