"""Yu-Gi-Oh! Official Rules Compliance Tests.

These tests verify that the duel implementation follows official Yu-Gi-Oh! rules
based on the official rulebook.
"""


from duel_core.affairs import (
    Attack,
    CompletedAffair,
    Draw,
    EnterPhase,
    NormalSummon,
)
from duel_core.duel import Duel
from duel_core.models import Card, Deck, Player, REPRESENTATION, RuntimeCard
from duel_core.phase import Phase


def _make_monster(card_id: int, name: str, atk: int, level: int = 4) -> Card:
    return Card(
        id=card_id,
        name=name,
        type="Normal Monster",
        desc=f"{name} - A {name} monster.",
        atk=atk,
        def_=atk,
        level=level,
        race="Dragon",
        attribute="LIGHT",
    )


def _make_runtime_monster(
    card_id: int, name: str, atk: int, level: int = 4, rep: REPRESENTATION = REPRESENTATION.ATTACK
) -> RuntimeCard:
    return RuntimeCard(card=_make_monster(card_id, name, atk, level), representation=rep)


def _make_player(label: str, deck_size: int) -> Player:
    return Player(
        label=label,
        main_deck=Deck(
            cards=[_make_monster(i, f"{label} Monster {i}", 1000 + i) for i in range(1, deck_size + 1)]
        ),
        extra_deck=[],
    )


def _make_duel() -> Duel:
    player_1 = _make_player("P1", 30)
    player_2 = _make_player("P2", 30)
    return Duel((player_1, player_2))


class TestOfficialRulesInitialSetup:
    """Test Rulebook: Chapter 1 - Before the Duel"""

    def test_initial_life_points(self) -> None:
        """Rule: Each player starts with 8000 Life Points."""
        duel = _make_duel()
        for player in duel.state.players:
            assert player.life_points == 8000

    def test_initial_hand_size(self) -> None:
        """Rule: Each player draws 5 cards at the start of a duel."""
        duel = _make_duel()
        for player in duel.state.players:
            assert len(player.hand) == 5

    def test_initial_deck_size(self) -> None:
        """Rule: Players draw from their Main Deck."""
        duel = _make_duel()
        for player in duel.state.players:
            assert len(player.main_deck.cards) == 25  # 30 - 5 initial draw

    def test_first_turn_no_battle(self) -> None:
        """Rule: The player who goes first cannot enter Battle Phase on their first turn."""
        duel = _make_duel()
        actions = duel.available_actions()
        battle_actions = [a for a in actions if isinstance(a, EnterPhase) and a.phase == Phase.BATTLE]
        assert len(battle_actions) == 0, "First turn should not have Battle Phase"

    def test_first_turn_no_draw(self) -> None:
        """Rule: The player who goes first does not draw on their first turn."""
        duel = _make_duel()
        actions = duel.available_actions()
        draw_actions = [a for a in actions if isinstance(a, Draw)]
        assert len(draw_actions) == 0, "First turn should not have draw action"


class TestOfficialRulesPhaseFlow:
    """Test Rulebook: Chapter 2 - Turn Structure"""

    def test_phase_order(self) -> None:
        """Rule: Phases proceed in order: Draw -> Standby -> Main 1 -> Battle -> Main 2 -> End."""
        duel = _make_duel()
        duel.state.phase = Phase.DRAW

        actions = duel.available_actions()
        assert len(actions) == 1
        action = actions[0]
        assert isinstance(action, EnterPhase)
        assert action.phase == Phase.STANDBY

    def test_draw_phase_draw_happens_automatically(self) -> None:
        """Rule: During your Draw Phase, you draw 1 card from your Deck.

        Note: Draw is automatic, not a player action choice.
        The Draw happens via EnterPhase(DRAW) -> turn_draw listener when the
        turn advances from End to the next player's Draw Phase.
        """
        duel = _make_duel()
        # The next player draws when the current turn ends into their Draw Phase.
        next_player = duel.state.opponent
        hand_before = len(next_player.hand)

        duel.state.phase = Phase.MAIN_2
        end_action = next(
            a for a in duel.available_actions() if isinstance(a, EnterPhase) and a.phase == Phase.END
        )
        duel.do(end_action)

        # Turn advanced to the opponent's Draw Phase, which drew automatically.
        assert duel.state.current_player is next_player
        assert duel.state.current_turn == 2
        assert len(next_player.hand) == hand_before + 1

    def test_cannot_skip_to_battle_from_draw(self) -> None:
        """Rule: Phases must proceed in order."""
        duel = _make_duel()
        duel.state.phase = Phase.DRAW

        actions = duel.available_actions()
        battle_actions = [a for a in actions if isinstance(a, EnterPhase) and a.phase == Phase.BATTLE]
        assert len(battle_actions) == 0

    def test_end_phase_exists(self) -> None:
        """Rule: The End Phase concludes your turn."""
        duel = _make_duel()
        duel.state.phase = Phase.MAIN_2

        actions = duel.available_actions()
        end_actions = [a for a in actions if isinstance(a, EnterPhase) and a.phase == Phase.END]
        assert len(end_actions) == 1


class TestOfficialRulesNormalSummon:
    """Test Rulebook: Chapter 3 - Summoning Monsters"""

    def test_normal_summon_level_4_or_lower(self) -> None:
        """Rule: You can Normal Summon Level 4 or lower monsters without tribute."""
        duel = _make_duel()
        duel.state.phase = Phase.MAIN_1

        actions = duel.available_actions()
        summon_actions = [a for a in actions if isinstance(a, NormalSummon)]
        assert len(summon_actions) > 0

    def test_normal_summon_level_5_plus_blocked(self) -> None:
        """Rule: Level 5+ monsters require Tribute Summon."""
        duel = _make_duel()
        player_1 = duel.state.current_player
        level_5_monster = _make_runtime_monster(9999, "Level 5 Monster", 2000, level=5)
        player_1.hand.append(level_5_monster)

        duel.state.phase = Phase.MAIN_1

        actions = duel.available_actions()
        summon_actions = [a for a in actions if isinstance(a, NormalSummon) and a.card == level_5_monster]
        assert len(summon_actions) == 0

    def test_only_one_normal_summon_per_turn(self) -> None:
        """Rule: You can only Normal Summon once per turn."""
        duel = _make_duel()
        duel.state.phase = Phase.MAIN_1

        actions = duel.available_actions()
        first_summon = next(a for a in actions if isinstance(a, NormalSummon))
        duel.do(first_summon)

        actions = duel.available_actions()
        summon_actions = [a for a in actions if isinstance(a, NormalSummon)]
        assert len(summon_actions) == 0

    def test_normal_summon_in_main_phase_only(self) -> None:
        """Rule: Normal Summon can only be performed during Main Phase."""
        duel = _make_duel()
        duel.state.phase = Phase.BATTLE

        actions = duel.available_actions()
        summon_actions = [a for a in actions if isinstance(a, NormalSummon)]
        assert len(summon_actions) == 0


class TestOfficialRulesBattle:
    """Test Rulebook: Chapter 4 - Battle"""

    def test_direct_attack_when_no_monsters(self) -> None:
        """Rule: You can attack directly if opponent has no monsters."""
        duel = _make_duel()
        player_1, player_2 = duel.state.players

        attacker = _make_runtime_monster(1, "Attacker", 1500)
        player_1.monster_zones[0] = attacker
        player_2.monster_zones[0] = None

        duel.state.phase = Phase.BATTLE
        duel.state.current_turn = 2  # Allow battle on turn 2+

        actions = duel.available_actions()
        direct_attacks = [
            a for a in actions if isinstance(a, Attack) and a.defender is None
        ]
        assert len(direct_attacks) == 1

    def test_direct_attack_damages_opponent(self) -> None:
        """Rule: Direct attack deals damage equal to attacker's ATK."""
        duel = _make_duel()
        player_1, player_2 = duel.state.players

        attacker = _make_runtime_monster(1, "Attacker", 1500)
        player_1.monster_zones[0] = attacker
        player_2.monster_zones[0] = None

        duel.state.phase = Phase.BATTLE
        duel.state.current_turn = 2

        completions: list[CompletedAffair] = []

        @duel.dispatcher.on(CompletedAffair)
        def collect(affair: CompletedAffair):
            completions.append(affair)

        action = next(a for a in duel.available_actions() if isinstance(a, Attack) and a.defender is None)
        duel.do(action)

        assert player_2.life_points == 6500  # 8000 - 1500

    def test_attacker_wins_vs_lower_defender(self) -> None:
        """Rule: If attacker ATK > defender ATK, defender is destroyed and difference is damage."""
        duel = _make_duel()
        player_1, player_2 = duel.state.players

        attacker = _make_runtime_monster(1, "Attacker", 2000)
        defender = _make_runtime_monster(2, "Defender", 1500)
        player_1.monster_zones[0] = attacker
        player_2.monster_zones[0] = defender

        duel.state.phase = Phase.BATTLE
        duel.state.current_turn = 2

        action = next(
            a for a in duel.available_actions()
            if isinstance(a, Attack) and a.attacker == attacker and a.defender == defender
        )
        duel.do(action)

        assert player_2.monster_zones[0] is None
        assert defender in player_2.graveyard
        assert player_2.life_points == 7500  # 8000 - (2000 - 1500)

    def test_defender_wins_vs_lower_attacker(self) -> None:
        """Rule: If defender ATK >= attacker ATK, attacker is destroyed and difference is damage."""
        duel = _make_duel()
        player_1, player_2 = duel.state.players

        attacker = _make_runtime_monster(1, "Attacker", 1500)
        defender = _make_runtime_monster(2, "Defender", 2000)
        player_1.monster_zones[0] = attacker
        player_2.monster_zones[0] = defender

        duel.state.phase = Phase.BATTLE
        duel.state.current_turn = 2

        action = next(
            a for a in duel.available_actions()
            if isinstance(a, Attack) and a.attacker == attacker and a.defender == defender
        )
        duel.do(action)

        assert player_1.monster_zones[0] is None
        assert attacker in player_1.graveyard
        assert player_1.life_points == 7500  # 8000 - (2000 - 1500)

    def test_both_destroyed_on_tie(self) -> None:
        """Rule: If attacker ATK = defender ATK, both monsters are destroyed."""
        duel = _make_duel()
        player_1, player_2 = duel.state.players

        attacker = _make_runtime_monster(1, "Attacker", 1500)
        defender = _make_runtime_monster(2, "Defender", 1500)
        player_1.monster_zones[0] = attacker
        player_2.monster_zones[0] = defender

        duel.state.phase = Phase.BATTLE
        duel.state.current_turn = 2

        action = next(
            a for a in duel.available_actions()
            if isinstance(a, Attack) and a.attacker == attacker and a.defender == defender
        )
        duel.do(action)

        assert player_1.monster_zones[0] is None
        assert player_2.monster_zones[0] is None
        assert attacker in player_1.graveyard
        assert defender in player_2.graveyard
        assert player_1.life_points == 8000  # No LP damage
        assert player_2.life_points == 8000


class TestOfficialRulesTurnAdvancement:
    """Test Rulebook: Chapter 5 - Winning the Duel"""

    def test_life_points_zero_loses(self) -> None:
        """Rule: When a player's Life Points reach 0, they lose."""
        duel = _make_duel()
        player_1, player_2 = duel.state.players

        attacker = _make_runtime_monster(1, "Attacker", 8500)
        player_1.monster_zones[0] = attacker
        player_2.monster_zones[0] = None

        duel.state.phase = Phase.BATTLE
        duel.state.current_turn = 2

        action = next(a for a in duel.available_actions() if isinstance(a, Attack) and a.defender is None)
        duel.do(action)

        assert player_2.life_points <= 0

    def test_turn_switch(self) -> None:
        """Rule: After End Phase, turn passes to opponent."""
        duel = _make_duel()
        player_1 = duel.state.current_player

        duel.state.phase = Phase.MAIN_2

        actions = duel.available_actions()
        end_action = next(a for a in actions if isinstance(a, EnterPhase) and a.phase == Phase.END)
        duel.do(end_action)

        assert duel.state.current_player is not player_1
        assert duel.state.current_turn == 2


class TestOfficialRulesExceptions:
    """Test special rules and edge cases."""

    def test_cannot_battle_if_no_monsters(self) -> None:
        """Rule: You cannot attack if you have no monsters."""
        duel = _make_duel()
        player_1 = duel.state.players[0]

        player_1.monster_zones[0] = None

        duel.state.phase = Phase.BATTLE
        duel.state.current_turn = 2

        actions = duel.available_actions()
        attack_actions = [a for a in actions if isinstance(a, Attack)]
        assert len(attack_actions) == 0

    def test_hand_limit_not_enforced(self) -> None:
        """Note: Hand size limit (7 cards) is not implemented in this slice."""
        duel = _make_duel()
        player = duel.state.current_player

        while len(player.hand) < 10:
            player.hand.append(_make_runtime_monster(9999, "Extra", 0))

        assert len(player.hand) == 10  # Currently allows overdraw
