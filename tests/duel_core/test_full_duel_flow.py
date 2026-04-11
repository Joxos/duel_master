"""Complete duel flow test integrating all assertions from isolated unit tests."""

from duel_core.affairs import (
    AdvanceTurn,
    Attack,
    CompletedAffair,
    Draw,
    EnterPhase,
    MoveCard,
    MultiAction,
    completed_affair_of,
    completed_multi_action_origin_of,
)
from duel_core.duel import Duel
from duel_core.models import Card, Deck, Player, REPRESENTATION, RuntimeCard
from duel_core.mr2020 import NormalSummon
from duel_core.phase import Phase


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


def _make_runtime_monster(card_id: int, name: str, atk: int, level: int = 4) -> RuntimeCard:
    return RuntimeCard(
        runtime_id=card_id,
        card=_make_monster(card_id, name, atk, level),
        representation=REPRESENTATION.ATTACK,
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


def test_complete_duel_flow() -> None:
    duel = _make_duel()
    player_1, player_2 = duel.state.players

    attack_completions: list[CompletedAffair] = []
    draw_completions: list[CompletedAffair] = []
    advance_turn_completions: list[CompletedAffair] = []
    end_phase_completions: list[CompletedAffair] = []

    @duel.dispatcher.on(CompletedAffair, when=completed_multi_action_origin_of(Attack))
    def track_attack_completion(affair: CompletedAffair) -> None:
        attack_completions.append(affair)

    @duel.dispatcher.on(CompletedAffair, when=completed_multi_action_origin_of(Draw))
    def track_draw_completion(affair: CompletedAffair) -> None:
        draw_completions.append(affair)

    @duel.dispatcher.on(CompletedAffair, when=completed_affair_of(AdvanceTurn))
    def track_advance_turn(affair: CompletedAffair) -> None:
        advance_turn_completions.append(affair)

    @duel.dispatcher.on(CompletedAffair, when=completed_affair_of(EnterPhase))
    def track_enter_phase(affair: CompletedAffair) -> None:
        if isinstance(affair.affair, EnterPhase) and affair.affair.phase is Phase.END:
            end_phase_completions.append(affair)

    assert len(player_1.hand) == 5
    assert len(player_2.hand) == 5
    assert duel.state.current_turn_count == 1
    assert duel.state.current_player is player_1
    assert duel.state.phase is Phase.DRAW

    view_p1 = duel.observe(player_1)
    assert view_p1.player_label == "P1"

    assert len(player_1.main_deck.cards) == 2
    assert len(player_2.main_deck.cards) == 2

    duel.do(
        next(
            action
            for action in duel.available_actions()
            if isinstance(action, EnterPhase) and action.phase is Phase.STANDBY
        )
    )
    assert duel.state.phase is Phase.STANDBY

    duel.do(
        next(
            action
            for action in duel.available_actions()
            if isinstance(action, EnterPhase) and action.phase is Phase.MAIN_1
        )
    )
    assert duel.state.phase is Phase.MAIN_1

    from duel_core.mr2020.rules import phase_actions

    battle_forbidden_check = EnterPhase(
        duel=duel,
        phase=Phase.BATTLE,
        source_phase=Phase.MAIN_1,
        requester=phase_actions,
    )
    assert duel.kernel.is_forbidden(battle_forbidden_check)

    p1_card = player_1.hand[0]
    p1_summon = NormalSummon(
        duel=duel,
        player=player_1,
        card=p1_card,
        to_zone=player_1.monster_zones[0],
        from_representation=p1_card.representation,
        to_representation=REPRESENTATION.ATTACK,
        normal_summon_used_from=False,
        normal_summon_used_to=True,
        requester=test_complete_duel_flow,
    )
    duel.do(p1_summon)

    assert player_1.monster_zones[0].card is p1_card
    assert duel.state.normal_summon_used

    duel.do(
        next(
            action
            for action in duel.available_actions()
            if isinstance(action, EnterPhase) and action.phase is Phase.END
        )
    )
    assert duel.state.phase is Phase.DRAW
    assert duel.state.current_turn_count == 2
    assert duel.state.current_player is player_2
    assert duel.state.normal_summon_used is False
    assert len(end_phase_completions) == 1
    assert len(advance_turn_completions) == 1

    # Turn 2 DRAW: turn_draw already fired (forbid expired), P2 has 6 cards
    assert len(player_2.hand) == 6
    assert len(player_2.main_deck.cards) == 1

    duel.do(
        next(
            action
            for action in duel.available_actions()
            if isinstance(action, EnterPhase) and action.phase is Phase.STANDBY
        )
    )
    assert duel.state.phase is Phase.STANDBY

    duel.do(
        next(
            action
            for action in duel.available_actions()
            if isinstance(action, EnterPhase) and action.phase is Phase.MAIN_1
        )
    )
    assert duel.state.phase is Phase.MAIN_1

    battle_action_turn2 = next(
        action
        for action in duel.available_actions()
        if isinstance(action, EnterPhase) and action.phase is Phase.BATTLE
    )
    assert not duel.kernel.is_forbidden(battle_action_turn2)

    p2_card = player_2.hand[0]
    p2_summon = NormalSummon(
        duel=duel,
        player=player_2,
        card=p2_card,
        to_zone=player_2.monster_zones[0],
        from_representation=p2_card.representation,
        to_representation=REPRESENTATION.ATTACK,
        normal_summon_used_from=False,
        normal_summon_used_to=True,
        requester=test_complete_duel_flow,
    )
    duel.do(p2_summon)

    assert player_2.monster_zones[0].card is p2_card

    duel.do(
        next(
            action
            for action in duel.available_actions()
            if isinstance(action, EnterPhase) and action.phase is Phase.BATTLE
        )
    )
    assert duel.state.phase is Phase.BATTLE

    p2_attack: Attack | None = None
    for action in duel.available_actions():
        if isinstance(action, Attack) and action.player is player_2:
            p2_attack = action
            break

    assert p2_attack is not None
    assert p2_attack.attacker is p2_card
    assert p2_attack.defender is not None
    assert p2_attack.defender is p1_card

    duel.do(p2_attack)

    assert len(attack_completions) == 1
    attack_completion = attack_completions[0]
    assert isinstance(attack_completion.affair, MultiAction)
    assert len(attack_completion.affair.children) == 2

    assert player_1.monster_zones[0].card is None

    draw_completion = next(
        (c for c in draw_completions if isinstance(c.affair, MultiAction)),
        None,
    )
    if draw_completion:
        affair = draw_completion.affair
        assert isinstance(affair, MultiAction)
        assert isinstance(affair.origin, Draw)
        assert all(isinstance(child, MoveCard) for child in affair.children)

    duel.do(
        next(
            action
            for action in duel.available_actions()
            if isinstance(action, EnterPhase) and action.phase is Phase.MAIN_2
        )
    )
    assert duel.state.phase is Phase.MAIN_2

    duel.do(
        next(
            action
            for action in duel.available_actions()
            if isinstance(action, EnterPhase) and action.phase is Phase.END
        )
    )
    assert duel.state.phase is Phase.DRAW
    assert duel.state.current_turn_count == 3
    assert len(end_phase_completions) == 2

    test_affair = MultiAction(
        duel=duel,
        requester=test_complete_duel_flow,
        origin=Draw(
            duel=duel,
            player=player_1,
            num=1,
            requester=test_complete_duel_flow,
        ),
        children=[],
    )
    assert test_affair.requester is test_complete_duel_flow
