from duel_core import Duel
from duel_core.mr2020.battle.affairs import Attack
from duel_core.mr2020.card.models import Card
from duel_core.mr2020.draw.affairs import Draw
from duel_core.mr2020.phase.affairs import EnterPhase
from duel_core.mr2020.phase.models import Phase
from duel_core.mr2020.player.models import Deck, Player
from duel_core.mr2020.summon.affairs import NormalSummon


def _make_monster(card_id: int, name: str, atk: int, level: int = 4) -> Card:
    return Card(
        database_id=card_id,
        name=name,
        type="Monster",
        desc=name,
        atk=atk,
        def_=atk,
        level=level,
        race="Dragon",
        attribute="LIGHT",
    )


def _make_duel() -> Duel:
    player_1 = Player(
        label="P1",
        main_deck=Deck(
            cards=[
                _make_monster(index, f"P1 Monster {index}", 1000 + index) for index in range(1, 8)
            ]
        ),
        extra_deck=Deck(cards=[]),
    )
    player_2 = Player(
        label="P2",
        main_deck=Deck(
            cards=[
                _make_monster(index + 100, f"P2 Monster {index}", 1000 + index)
                for index in range(1, 8)
            ]
        ),
        extra_deck=Deck(cards=[]),
    )
    return Duel((player_1, player_2), starting_player=player_1)


def _phase_action(duel: Duel, target: Phase) -> EnterPhase:
    return next(
        action
        for action in duel.available_actions()
        if isinstance(action, EnterPhase) and action.phase is target
    )


def test_smoke_duel_loop() -> None:
    duel = _make_duel()
    player_1, player_2 = duel.state.get_players()

    assert len(player_1.hand) == 5
    assert len(player_2.hand) == 5
    assert len(player_1.main_deck.cards) == 2
    assert len(player_2.main_deck.cards) == 2
    assert duel.state.get_current_turn_count() == 1
    assert duel.state.get_current_player() is player_1
    assert duel.state.get_phase() is Phase.DRAW

    view = duel.observe(player_1)
    assert view.player_label == "P1"
    assert view.public.current_player_label == "P1"
    assert len(view.hand) == 5
    assert len(view.public.players) == 2

    draw_actions = [action for action in duel.available_actions() if isinstance(action, Draw)]
    assert not draw_actions

    duel.do(_phase_action(duel, Phase.STANDBY))
    assert duel.state.get_phase() is Phase.STANDBY

    duel.do(_phase_action(duel, Phase.MAIN_1))
    assert duel.state.get_phase() is Phase.MAIN_1

    main_1_actions = duel.available_actions()
    assert not any(
        isinstance(action, EnterPhase) and action.phase is Phase.BATTLE for action in main_1_actions
    )

    summon_action = next(action for action in main_1_actions if isinstance(action, NormalSummon))
    summoned_card = summon_action.card
    duel.do(summon_action)

    assert player_1.monster_zones[0].card is summoned_card
    assert duel.state.get_normal_summon_used() is True

    duel.do(_phase_action(duel, Phase.END))
    assert duel.state.get_phase() is Phase.DRAW
    assert duel.state.get_current_turn_count() == 2
    assert duel.state.get_current_player() is player_2
    assert duel.state.get_normal_summon_used() is False
    assert len(player_2.hand) == 6
    assert len(player_2.main_deck.cards) == 1

    duel.do(_phase_action(duel, Phase.STANDBY))
    duel.do(_phase_action(duel, Phase.MAIN_1))

    turn_2_main_actions = duel.available_actions()
    assert any(
        isinstance(action, EnterPhase) and action.phase is Phase.BATTLE
        for action in turn_2_main_actions
    )

    p2_summon = next(
        action
        for action in turn_2_main_actions
        if isinstance(action, NormalSummon)
        and action.card.card.atk is not None
        and summoned_card.card.atk is not None
        and action.card.card.atk > summoned_card.card.atk
    )
    p2_card = p2_summon.card
    duel.do(p2_summon)
    assert player_2.monster_zones[0].card is p2_card

    duel.do(_phase_action(duel, Phase.BATTLE))
    assert duel.state.get_phase() is Phase.BATTLE

    attack_action = next(
        action for action in duel.available_actions() if isinstance(action, Attack)
    )
    assert attack_action.attacker is p2_card
    assert attack_action.defender is summoned_card

    duel.do(attack_action)
    assert player_1.monster_zones[0].card is None
    assert player_1.life_points < 8000

    duel.do(_phase_action(duel, Phase.MAIN_2))
    assert duel.state.get_phase() is Phase.MAIN_2

    duel.do(_phase_action(duel, Phase.END))
    assert duel.state.get_phase() is Phase.DRAW
    assert duel.state.get_current_turn_count() == 3
