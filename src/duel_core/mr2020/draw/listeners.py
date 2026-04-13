from __future__ import annotations

from affairon import listen

from duel_core.mr2020.card.affairs import MoveCard
from duel_core.mr2020.card.listeners import apply_move_card, normalize_runtime_cards
from duel_core.mr2020.draw.affairs import Draw
from duel_core.mr2020.duel.affairs import CompletedAffair, DuelInit, MultiAction
from duel_core.mr2020.forbid.affairs import Forbid
from duel_core.mr2020.forbid.listeners import inject_active_forbids
from duel_core.mr2020.phase.models import Phase
from duel_core.mr2020.timing.affairs import AtomicAction
from duel_core.mr2020.timing.predicates import completed_enter_phase

INITIAL_DRAW_NUM = 5
TURN_DRAW_NUM = 1


@listen(DuelInit, after=[normalize_runtime_cards])
def initial_draw(affair: DuelInit) -> None:
    for player in affair.duel.get_players():
        affair.duel.do(
            Draw(
                duel=affair.duel,
                player=player,
                num=INITIAL_DRAW_NUM,
                requester=initial_draw,
            )
        )


@listen(DuelInit, after=[inject_active_forbids])
def forbid_initial_turn_draw(affair: DuelInit) -> None:
    affair.duel.emit(
        Forbid(
            duel=affair.duel,
            target=Draw(
                duel=affair.duel,
                player=affair.duel.get_current_player(),
                num=TURN_DRAW_NUM,
                requester=turn_draw,
            ),
            inactive_from_turn=affair.duel.get_current_turn_count() + 1,
        )
    )


@listen(CompletedAffair, when=completed_enter_phase(Phase.DRAW))
def turn_draw(completed: CompletedAffair) -> None:
    affair = completed.affair
    affair.duel.do(
        Draw(
            duel=affair.duel,
            player=affair.duel.get_current_player(),
            num=TURN_DRAW_NUM,
            requester=turn_draw,
        )
    )


@listen(Draw)
def plan_draw(affair: Draw) -> None:
    drawn = affair.player.main_deck.draw(affair.num)
    affair.player.main_deck.cards = drawn + affair.player.main_deck.cards

    children: list[AtomicAction] = [
        MoveCard(
            duel=affair.duel,
            player=affair.player,
            card=card,
            from_area="main_deck",
            to_area="hand",
            from_representation=card.representation,
            to_representation=card.representation,
        )
        for card in drawn
    ]

    multi = MultiAction(
        duel=affair.duel,
        requester=affair.requester,
        origin=affair,
        children=children,
    )
    for child in multi.children:
        assert isinstance(child, MoveCard)
        apply_move_card(child)
    affair.duel.emit(CompletedAffair(duel=affair.duel, affair=multi))
