from duel_core import CompletedAffair, Deck, Duel, ExecutableAffair, Player


def build_duel() -> Duel:
    return Duel(
        players=(
            Player(main_deck=Deck(cards=[f"p1-{i}" for i in range(10)]), extra_deck=Deck(cards=[])),
            Player(main_deck=Deck(cards=[f"p2-{i}" for i in range(10)]), extra_deck=Deck(cards=[])),
        )
    )


def test_do_end_turn_advances_turn_and_emits_completed_affair() -> None:
    duel = build_duel()
    first_player = duel.current_player
    completed: list[ExecutableAffair] = []

    @duel.dispatcher.on(CompletedAffair)
    def capture_completion(affair: CompletedAffair) -> None:
        completed.append(affair.affair)

    action = duel.available_actions()[0]

    duel.do(action)

    assert duel.current_turn == 2
    assert duel.current_player is not first_player
    assert duel.phase.value == "Draw"
    assert completed == [action]
