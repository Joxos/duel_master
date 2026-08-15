from __future__ import annotations

from typing import cast

from affairon import listen

from duel_core.mr2020.card.affairs import MoveCard
from duel_core.mr2020.card.models import RuntimeCard
from duel_core.mr2020.card.listeners import normalize_runtime_cards
from duel_core.mr2020.draw.affairs import Draw
from duel_core.mr2020.duel.affairs import CompletedAffair, DuelInit, MultiAction
from duel_core.mr2020.forbid.affairs import Forbid
from duel_core.mr2020.forbid.listeners import setup_forbid_runtime
from duel_core.mr2020.phase.models import Phase
from duel_core.mr2020.player.runtime import PlayerRuntime
from duel_core.mr2020.timing.affairs import AtomicAction
from duel_core.mr2020.timing.predicates import completed_enter_phase
from duel_core.mr2020.turn.runtime import TurnRuntime

INITIAL_DRAW_NUM = 5
TURN_DRAW_NUM = 1


@listen(DuelInit, after=[setup_forbid_runtime, normalize_runtime_cards])
def initial_draw(affair: DuelInit) -> None:
    for player in affair.duel.inject(PlayerRuntime).players:
        affair.duel.do(
            Draw(
                duel=affair.duel,
                player=player,
                num=INITIAL_DRAW_NUM,
                requester=initial_draw,
            )
        )


@listen(DuelInit, after=[setup_forbid_runtime])
def forbid_initial_turn_draw(affair: DuelInit) -> None:
    player_runtime = affair.duel.inject(PlayerRuntime)
    turn_runtime = affair.duel.inject(TurnRuntime)
    affair.duel.emit(
        Forbid(
            duel=affair.duel,
            target=Draw(
                duel=affair.duel,
                player=player_runtime.current_player,
                num=TURN_DRAW_NUM,
                requester=turn_draw,
            ),
            inactive_from_turn=turn_runtime.current_turn_count + 1,
        )
    )


@listen(CompletedAffair, when=completed_enter_phase(Phase.DRAW))
def turn_draw(completed: CompletedAffair) -> None:
    affair = completed.affair
    player_runtime = affair.duel.inject(PlayerRuntime)
    affair.duel.do(
        Draw(
            duel=affair.duel,
            player=player_runtime.current_player,
            num=TURN_DRAW_NUM,
            requester=turn_draw,
        )
    )


@listen(Draw)
def plan_draw(affair: Draw) -> None:
    drawn = cast(list[RuntimeCard], affair.player.main_deck.cards[: affair.num])

    children: list[AtomicAction] = []
    for runtime_card in drawn:
        children.append(
            MoveCard(
                duel=affair.duel,
                player=affair.player,
                card=runtime_card,
                from_area="main_deck",
                to_area="hand",
                from_representation=runtime_card.representation,
                to_representation=runtime_card.representation,
            )
        )

    multi = MultiAction(
        duel=affair.duel,
        requester=affair.requester,
        origin=affair,
        children=children,
    )
    affair.duel.emit(multi)
