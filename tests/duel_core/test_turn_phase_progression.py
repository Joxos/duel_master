from duel_core import Deck, Duel, Phase, Player


def build_duel() -> Duel:
    return Duel(
        players=(
            Player(main_deck=Deck(cards=[f"p1-{i}" for i in range(10)]), extra_deck=Deck(cards=[])),
            Player(main_deck=Deck(cards=[f"p2-{i}" for i in range(10)]), extra_deck=Deck(cards=[])),
        )
    )


def test_first_turn_progresses_from_draw_to_main_phase_1() -> None:
    duel = build_duel()

    labels = [str(action) for action in duel.available_actions()]
    assert labels == ["Enter Standby Phase"]

    duel.do(duel.available_actions()[0])
    assert duel.state.phase is Phase.STANDBY

    labels = [str(action) for action in duel.available_actions()]
    assert labels == ["Enter Main Phase 1"]

    duel.do(duel.available_actions()[0])
    assert duel.state.phase is Phase.MAIN_1


def test_first_turn_cannot_enter_battle_phase() -> None:
    duel = build_duel()

    duel.do(duel.available_actions()[0])
    duel.do(duel.available_actions()[0])

    labels = [str(action) for action in duel.available_actions()]

    assert "Enter Battle Phase" not in labels
    assert "Enter End Phase" in labels


def test_later_turn_can_enter_battle_and_main_phase_2() -> None:
    duel = build_duel()

    duel.do(duel.available_actions()[0])
    duel.do(duel.available_actions()[0])
    end_action = next(
        action for action in duel.available_actions() if str(action) == "Enter End Phase"
    )
    duel.do(end_action)
    duel.do(duel.available_actions()[0])

    duel.do(duel.available_actions()[0])

    labels = [str(action) for action in duel.available_actions()]
    assert "Enter Battle Phase" in labels

    battle_action = next(
        action for action in duel.available_actions() if str(action) == "Enter Battle Phase"
    )
    duel.do(battle_action)
    assert duel.state.phase is Phase.BATTLE

    labels = [str(action) for action in duel.available_actions()]
    assert labels == ["Enter Main Phase 2"]


def test_end_turn_still_advances_to_next_players_draw_phase() -> None:
    duel = build_duel()

    duel.do(duel.available_actions()[0])
    duel.do(duel.available_actions()[0])
    end_action = next(
        action for action in duel.available_actions() if str(action) == "Enter End Phase"
    )
    duel.do(end_action)

    assert duel.state.current_turn == 2
    assert duel.state.current_player is duel.state.players[1]
    assert duel.state.phase is Phase.DRAW
