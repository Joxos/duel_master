from duel_core.affairs import CompletedAffair, Draw, MultiAffair
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
        main_deck=Deck(
            cards=[
                _make_monster(index, f"P1 Monster {index}", 1000 + index) for index in range(1, 8)
            ]
        ),
        extra_deck=[],
    )
    player_2 = Player(
        label="P2",
        main_deck=Deck(
            cards=[
                _make_monster(index + 100, f"P2 Monster {index}", 1000 + index)
                for index in range(1, 8)
            ]
        ),
        extra_deck=[],
    )
    return Duel((player_1, player_2))


def test_attack_completion_carries_multi_affair_result() -> None:
    duel = _make_duel()
    player_1, player_2 = duel.state.players

    attacker_card = _make_runtime_monster(1000, "Blue-Eyes White Dragon", 3000)
    defender_card = _make_runtime_monster(1001, "Battle Ox", 1700)
    player_1.monster_zones[0] = attacker_card
    player_2.monster_zones[0] = defender_card
    duel.state.phase = Phase.BATTLE

    completions: list[CompletedAffair] = []

    @duel.dispatcher.on(CompletedAffair)
    def collect_completion(affair: CompletedAffair) -> None:
        completions.append(affair)

    action = next(a for a in duel.available_actions() if a.__class__.__name__ == "Attack")
    duel.do(action)

    assert len(completions) == 1
    completion = completions[0]
    assert completion.action == action
    assert isinstance(completion.result, MultiAffair)
    assert len(completion.result.children) == 2
    assert player_2.monster_zones[0] is None
    assert player_2.life_points == 6700


def test_multi_affair_keeps_requester_identity() -> None:
    duel = _make_duel()

    affair = MultiAffair(
        duel=duel, requester=test_multi_affair_keeps_requester_identity, children=[]
    )

    assert affair.requester is test_multi_affair_keeps_requester_identity


def test_draw_completion_result_is_draw_itself() -> None:
    duel = _make_duel()
    current_player = duel.state.current_player
    completions: list[CompletedAffair] = []

    @duel.dispatcher.on(CompletedAffair)
    def collect_completion(affair: CompletedAffair) -> None:
        completions.append(affair)

    draw_action = next(
        Draw(
            duel=duel,
            player=current_player,
            num=1,
            requester=test_draw_completion_result_is_draw_itself,
        )
        for _ in range(1)
    )
    hand_before = len(current_player.hand)
    duel.emit(draw_action)

    assert len(completions) == 1
    completion = completions[0]
    assert completion.action == draw_action
    assert completion.result == draw_action
    assert len(current_player.hand) == hand_before + 1
