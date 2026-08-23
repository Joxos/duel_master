"""Tests for Master Rule 2020 win conditions (rulebook chapter 5).

These tests verify the official victory conditions implemented by the
``mr2020_win`` plugin:

- a player loses when their Life Points reach 0 or below
- a player loses when the Draw Phase starts with an empty deck
- a player loses when they concede
- no actions are offered once the duel has ended
"""

from duel_core.affairs import Concede, EnterPhase, MatchEnd
from duel_core.duel import Duel
from duel_core.models import Card, Deck, Player, REPRESENTATION, RuntimeCard
from duel_core.phase import Phase


def _make_monster(card_id: int, name: str, atk: int) -> Card:
    return Card(
        id=card_id,
        name=name,
        type="Monster",
        desc=name,
        atk=atk,
        def_=atk,
        level=4,
        race="Dragon",
        attribute="LIGHT",
    )


def _make_runtime_monster(card_id: int, name: str, atk: int) -> RuntimeCard:
    return RuntimeCard(
        card=_make_monster(card_id, name, atk),
        representation=REPRESENTATION.ATTACK,
    )


def _make_duel() -> Duel:
    player_1 = Player(
        label="P1",
        main_deck=Deck(cards=[_make_monster(i, f"P1 {i}", 1000) for i in range(1, 11)]),
        extra_deck=[],
    )
    player_2 = Player(
        label="P2",
        main_deck=Deck(cards=[_make_monster(i, f"P2 {i}", 1000) for i in range(1, 11)]),
        extra_deck=[],
    )
    return Duel((player_1, player_2))


def _match_end_events(duel: Duel) -> list[MatchEnd]:
    events: list[MatchEnd] = []

    @duel.dispatcher.on(MatchEnd)
    def collect(affair: MatchEnd) -> None:
        events.append(affair)

    return events


class TestLifePointsWinCondition:
    """Rulebook chapter 5: losing when Life Points reach 0."""

    def test_direct_attack_to_zero_loses(self) -> None:
        duel = _make_duel()
        player_1, player_2 = duel.state.players
        events = _match_end_events(duel)

        attacker = _make_runtime_monster(1000, "Attacker", 8500)
        player_1.monster_zones[0] = attacker
        player_2.monster_zones[0] = None
        duel.state.phase = Phase.BATTLE
        duel.state.current_turn = 2

        action = next(
            a for a in duel.available_actions()
            if type(a).__name__ == "Attack" and a.defender is None
        )
        duel.do(action)

        assert len(events) == 1
        assert events[0].reason == "life_points_zero"
        assert events[0].winner is player_1
        assert events[0].loser is player_2
        assert duel.state.game_over
        assert duel.state.winner is player_1

    def test_available_actions_empty_after_match_end(self) -> None:
        duel = _make_duel()
        player_1, player_2 = duel.state.players

        attacker = _make_runtime_monster(1000, "Attacker", 8500)
        player_1.monster_zones[0] = attacker
        player_2.monster_zones[0] = None
        duel.state.phase = Phase.BATTLE
        duel.state.current_turn = 2

        attack = next(
            a for a in duel.available_actions()
            if type(a).__name__ == "Attack" and a.defender is None
        )
        duel.do(attack)

        assert duel.available_actions() == []


class TestDeckEmptyWinCondition:
    """Rulebook chapter 5: losing when the Draw Phase starts with an empty deck."""

    def test_empty_deck_on_draw_phase_loses(self) -> None:
        duel = _make_duel()
        player_1, player_2 = duel.state.players
        events = _match_end_events(duel)

        # Clear P2's deck so P2 loses when their turn 2 Draw Phase begins.
        player_2.main_deck.cards.clear()

        duel.state.phase = Phase.MAIN_2
        end_action = next(
            a for a in duel.available_actions()
            if isinstance(a, EnterPhase) and a.phase is Phase.END
        )
        duel.do(end_action)

        assert len(events) == 1
        assert events[0].reason == "deck_empty"
        assert events[0].winner is player_1
        assert events[0].loser is player_2
        assert duel.state.game_over


class TestConcedeWinCondition:
    """Rulebook chapter 5: losing when a player concedes."""

    def test_concede_declares_opponent_winner(self) -> None:
        duel = _make_duel()
        player_1, player_2 = duel.state.players
        events = _match_end_events(duel)

        duel.emit(Concede(duel=duel, player=player_1))

        assert len(events) == 1
        assert events[0].reason == "concede"
        assert events[0].winner is player_2
        assert events[0].loser is player_1
        assert duel.state.game_over
        assert duel.state.winner is player_2


class TestNoFalsePositives:
    """No win condition should fire during normal play."""

    def test_normal_duel_does_not_end(self) -> None:
        duel = _make_duel()
        events = _match_end_events(duel)

        duel.state.phase = Phase.MAIN_1
        summon = next(a for a in duel.available_actions() if type(a).__name__ == "NormalSummon")
        duel.do(summon)

        assert events == []
        assert not duel.state.game_over
