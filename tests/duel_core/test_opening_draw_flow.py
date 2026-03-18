from duel_core import Deck, Duel, EnterPhase, ExitPhase, Phase, Player
from duel_core.mr2020 import INITIAL_DRAW_NUM, TURN_DRAW_NUM


def phase_requester(*_args: object, **_kwargs: object) -> object:
    return None


def build_duel() -> Duel:
    return Duel(
        players=(
            Player(main_deck=Deck(cards=[f"p1-{i}" for i in range(10)]), extra_deck=Deck(cards=[])),
            Player(main_deck=Deck(cards=[f"p2-{i}" for i in range(10)]), extra_deck=Deck(cards=[])),
        )
    )


def test_duel_init_draws_initial_hands() -> None:
    duel = build_duel()

    assert duel.current_player is duel.players[0]
    assert duel.players[0].hand == [f"p1-{i}" for i in range(INITIAL_DRAW_NUM)]
    assert duel.players[1].hand == [f"p2-{i}" for i in range(INITIAL_DRAW_NUM)]


def test_first_draw_phase_is_forbidden_for_opening_player() -> None:
    duel = build_duel()

    try:
        duel.emit(EnterPhase(duel=duel, phase=Phase.DRAW, requester=phase_requester))
    except ValueError as exc:
        assert "Affair is forbidden" in str(exc)
    else:
        raise AssertionError("expected opening draw to fail fast when forbidden")


def test_later_draw_phase_draws_one_card_after_cleanup() -> None:
    duel = build_duel()
    try:
        duel.emit(EnterPhase(duel=duel, phase=Phase.DRAW, requester=phase_requester))
    except ValueError as exc:
        assert "Affair is forbidden" in str(exc)
    else:
        raise AssertionError("expected opening draw to fail fast before cleanup")

    next_player = duel.players[1]
    before = len(next_player.hand)

    duel.emit(ExitPhase(duel=duel, phase=Phase.END, requester=phase_requester))

    assert len(next_player.hand) == before + TURN_DRAW_NUM


def test_unknown_user_action_is_rejected() -> None:
    duel = build_duel()

    def unknown_requester(*_args: object, **_kwargs: object) -> object:
        return None

    try:
        duel.do(
            EnterPhase(
                label="Unknown action",
                duel=duel,
                phase=Phase.DRAW,
                requester=unknown_requester,
            )
        )
    except ValueError as exc:
        assert "Unknown action" in str(exc)
    else:
        raise AssertionError("expected unknown action to be rejected")
