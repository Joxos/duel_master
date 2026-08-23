"""Master Rule 2020 win conditions for the current duel slice.

This plugin observes duel progress and emits ``MatchEnd`` affairs when an
official win condition is satisfied, per the rulebook chapter 5:

- a player's Life Points reach 0 or below
- a player must draw from an empty deck during the Draw Phase
- a player concedes the duel

Kernel owns the final match-state mutation; this plugin only declares the
outcome through affairs.
"""

from typing import TYPE_CHECKING

from affairon.listen import listen

from duel_core.affairs import (
    AvailableActions,
    CompletedAffair,
    Concede,
    EnterPhase,
    MatchEnd,
)
from duel_core.models import Player
from duel_core.phase import Phase

if TYPE_CHECKING:
    from duel_core.duel import Duel


def _emit_match_end(duel: "Duel", *, winner: Player, loser: Player, reason: str) -> None:
    duel.emit(MatchEnd(duel=duel, winner=winner, loser=loser, reason=reason))


@listen(Concede)
def declare_concede(affair: Concede) -> None:
    """Rule: A player loses when they voluntarily concede the duel."""
    state = affair.duel.state
    if state.game_over:
        return
    _emit_match_end(
        affair.duel,
        winner=state.opponent_of(affair.player),
        loser=affair.player,
        reason="concede",
    )


@listen(CompletedAffair)
def check_life_points_zero(affair: CompletedAffair) -> None:
    """Rule: A player loses when their Life Points reach 0 or below."""
    state = affair.duel.state
    if state.game_over:
        return
    for player in state.players:
        if player.life_points <= 0:
            _emit_match_end(
                affair.duel,
                winner=state.opponent_of(player),
                loser=player,
                reason="life_points_zero",
            )
            return


@listen(EnterPhase)
def check_deck_empty_on_draw(affair: EnterPhase) -> None:
    """Rule: A player loses when the Draw Phase starts with an empty deck."""
    state = affair.duel.state
    if state.game_over:
        return
    if affair.phase is not Phase.DRAW:
        return
    current_player = state.current_player
    if not current_player.main_deck.cards:
        _emit_match_end(
            affair.duel,
            winner=state.opponent_of(current_player),
            loser=current_player,
            reason="deck_empty",
        )


@listen(AvailableActions)
def suppress_actions_after_match_end(affair: AvailableActions) -> None:
    """Guard: No actions are offered once the duel has ended."""
    if affair.duel.state.game_over:
        affair.actions.clear()
