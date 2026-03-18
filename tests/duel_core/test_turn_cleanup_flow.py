from duel_core import CompletedAffair, Deck, Duel, ExecutableAffair, Phase, Player


def build_duel() -> Duel:
    return Duel(
        players=(
            Player(main_deck=Deck(cards=[f"p1-{i}" for i in range(10)]), extra_deck=Deck(cards=[])),
            Player(main_deck=Deck(cards=[f"p2-{i}" for i in range(10)]), extra_deck=Deck(cards=[])),
        )
    )


def test_do_end_turn_advances_turn_and_emits_completed_affair() -> None:
    duel = build_duel()
    first_player = duel.state.current_player
    completed: list[ExecutableAffair] = []

    @duel.dispatcher.on(CompletedAffair)
    def capture_completion(affair: CompletedAffair) -> None:
        completed.append(affair.affair)

    duel.do(duel.available_actions()[0])
    duel.do(duel.available_actions()[0])
    end_phase_action = next(
        action for action in duel.available_actions() if str(action) == "Enter End Phase"
    )
    duel.do(end_phase_action)

    assert duel.state.current_turn == 2
    assert duel.state.current_player is not first_player
    assert duel.state.phase is Phase.DRAW
    assert completed[-1] == end_phase_action
