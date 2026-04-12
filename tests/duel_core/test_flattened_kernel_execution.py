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
from duel_core.mr2020.actions import NormalSummon
from duel_core.mr2020.models import Card, Deck, Player, REPRESENTATION, RuntimeCard
from duel_core.phase import Phase


def _make_monster(card_id: int, name: str, atk: int) -> Card:
    return Card(
        database_id=card_id,
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
        runtime_id=card_id,
        card=_make_monster(card_id, name, atk),
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


def test_attack_completion_is_multi_affair() -> None:
    duel = _make_duel()
    player_1, player_2 = duel.state.players

    attacker_card = _make_runtime_monster(1000, "Blue-Eyes White Dragon", 3000)
    defender_card = _make_runtime_monster(1001, "Battle Ox", 1700)
    player_1.monster_zones[0].card = attacker_card
    player_2.monster_zones[0].card = defender_card
    duel.state.phase = Phase.BATTLE

    completions: list[CompletedAffair] = []

    @duel.dispatcher.on(CompletedAffair, when=completed_multi_action_origin_of(Attack))
    def collect_completion(affair: CompletedAffair) -> None:
        completions.append(affair)

    action = next(a for a in duel.available_actions() if a.__class__.__name__ == "Attack")
    duel.do(action)

    assert len(completions) == 1
    completion = completions[0]
    assert isinstance(completion.affair, MultiAction)
    assert len(completion.affair.children) == 2
    assert player_2.monster_zones[0].card is None
    assert player_2.life_points == 6700


def test_multi_action_keeps_requester_identity() -> None:
    duel = _make_duel()

    affair = MultiAction(
        duel=duel,
        requester=test_multi_action_keeps_requester_identity,
        origin=Draw(
            duel=duel,
            player=duel.state.current_player,
            num=1,
            requester=test_multi_action_keeps_requester_identity,
        ),
        children=[],
    )

    assert affair.requester is test_multi_action_keeps_requester_identity


def test_draw_completion_affair_is_draw_itself() -> None:
    duel = _make_duel()
    current_player = duel.state.current_player
    completions: list[CompletedAffair] = []

    @duel.dispatcher.on(CompletedAffair, when=completed_multi_action_origin_of(Draw))
    def collect_completion(affair: CompletedAffair) -> None:
        completions.append(affair)

    draw_action = next(
        Draw(
            duel=duel,
            player=current_player,
            num=1,
            requester=test_draw_completion_affair_is_draw_itself,
        )
        for _ in range(1)
    )
    hand_before = len(current_player.hand)
    duel.do(draw_action)

    assert len(completions) == 1
    completion = completions[0]
    assert isinstance(completion.affair, MultiAction)
    assert completion.affair.origin == draw_action
    assert len(current_player.hand) == hand_before + 1


def test_end_phase_completes_before_draw_progression() -> None:
    duel = _make_duel()
    duel.state.phase = Phase.MAIN_1

    end_completions: list[CompletedAffair] = []

    @duel.dispatcher.on(CompletedAffair, when=completed_affair_of(EnterPhase))
    def collect_enter_phase_completion(affair: CompletedAffair) -> None:
        if isinstance(affair.affair, EnterPhase) and affair.affair.phase is Phase.END:
            end_completions.append(affair)
            assert duel.state.phase is Phase.END

    end_action = next(
        action
        for action in duel.available_actions()
        if isinstance(action, EnterPhase) and action.phase is Phase.END
    )

    duel.do(end_action)

    assert len(end_completions) == 1


def test_turn_rollover_expires_forbids_and_draws_next_card() -> None:
    duel = _make_duel()
    player_1, player_2 = duel.state.players
    duel.state.phase = Phase.MAIN_1

    advance_turn_completions: list[CompletedAffair] = []
    draw_completions: list[CompletedAffair] = []
    player_2_hand_before = len(player_2.hand)

    @duel.dispatcher.on(CompletedAffair, when=completed_affair_of(AdvanceTurn))
    def collect_advance_turn(affair: CompletedAffair) -> None:
        advance_turn_completions.append(affair)

    @duel.dispatcher.on(CompletedAffair, when=completed_multi_action_origin_of(Draw))
    def collect_turn_draw(affair: CompletedAffair) -> None:
        draw_completions.append(affair)

    end_action = next(
        action
        for action in duel.available_actions()
        if isinstance(action, EnterPhase) and action.phase is Phase.END
    )
    duel.do(end_action)

    assert len(advance_turn_completions) == 1
    assert len(draw_completions) >= 1
    assert duel.state.current_turn_count == 2
    assert duel.state.current_player is player_2
    assert duel.state.phase is Phase.DRAW
    assert len(player_2.hand) == player_2_hand_before + 1
    battle_action = EnterPhase(
        duel=duel,
        phase=Phase.BATTLE,
        source_phase=Phase.MAIN_1,
        requester=duel.available_actions,
    )
    assert not duel.kernel.is_forbidden(battle_action)


def test_observe_accepts_original_player_identity() -> None:
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
    duel = Duel((player_1, player_2), starting_player=player_1)

    view = duel.observe(player_1)

    assert view.player_label == "P1"
    assert view.public.players[0].label == "P1"


def test_manual_normal_summon_applies_without_execution_recheck() -> None:
    duel = _make_duel()
    player = duel.state.current_player
    duel.state.phase = Phase.MAIN_1
    duel.state.normal_summon_used = True

    card = player.hand[0]
    action = NormalSummon(
        duel=duel,
        player=player,
        card=card,
        to_zone=player.monster_zones[0],
        from_representation=card.representation,
        to_representation=REPRESENTATION.ATTACK,
        normal_summon_used_from=True,
        normal_summon_used_to=True,
        requester=test_manual_normal_summon_applies_without_execution_recheck,
    )

    duel.do(action)

    assert player.monster_zones[0].card is card


def test_draw_completion_uses_multi_affair_origin_without_index_payload() -> None:
    duel = _make_duel()
    current_player = duel.state.current_player
    completions: list[CompletedAffair] = []

    @duel.dispatcher.on(CompletedAffair, when=completed_multi_action_origin_of(Draw))
    def collect_completion(affair: CompletedAffair) -> None:
        completions.append(affair)

    draw_action = Draw(
        duel=duel,
        player=current_player,
        num=2,
        requester=test_draw_completion_uses_multi_affair_origin_without_index_payload,
    )

    duel.do(draw_action)

    assert len(completions) == 1
    completion = completions[0]
    assert isinstance(completion.affair, MultiAction)
    assert completion.affair.origin == draw_action
    assert all(isinstance(child, MoveCard) for child in completion.affair.children)


def test_public_view_derives_battle_state_from_phase() -> None:
    duel = _make_duel()
    duel.state.phase = Phase.BATTLE

    view = duel.observe(duel.state.current_player)

    assert view.public.phase is Phase.BATTLE


def test_observe_exposes_public_and_private_information() -> None:
    duel = _make_duel()

    view = duel.observe(duel.state.current_player)

    assert view.player_label == duel.state.current_player.label
    assert len(view.hand) == len(duel.state.current_player.hand)
    assert len(view.public.players) == 2
