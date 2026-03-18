from duel_core import Deck, Duel, Player


def build_duel() -> Duel:
    return Duel(
        players=(
            Player(main_deck=Deck(cards=[f"p1-{i}" for i in range(10)]), extra_deck=Deck(cards=[])),
            Player(main_deck=Deck(cards=[f"p2-{i}" for i in range(10)]), extra_deck=Deck(cards=[])),
        )
    )


def test_duel_exposes_kernel_state() -> None:
    duel = build_duel()

    assert duel.state is duel.kernel.state
    assert duel.state.current_player is duel.state.players[0]
    assert duel.state.current_turn == 1
    assert duel.state.phase.value == "Draw"
