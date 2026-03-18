from duel_core import Deck, Duel, EnterPhase, ExecutableAffair, Player
from duel_core.affairs import AvailableActions


def build_duel() -> Duel:
    return Duel(
        players=(
            Player(main_deck=Deck(cards=[f"p1-{i}" for i in range(10)]), extra_deck=Deck(cards=[])),
            Player(main_deck=Deck(cards=[f"p2-{i}" for i in range(10)]), extra_deck=Deck(cards=[])),
        )
    )


def test_observe_returns_renderable_view_for_current_player() -> None:
    duel = build_duel()

    view = duel.observe(view=duel.state.current_player)

    assert view.viewer is duel.state.current_player
    assert view.public.current_player is duel.state.current_player


def test_available_actions_returns_executable_affairs() -> None:
    duel = build_duel()

    actions = duel.available_actions()

    assert all(isinstance(action, ExecutableAffair) for action in actions)
    assert str(actions[0]) == "Enter Standby Phase"


def test_available_actions_are_collected_via_dispatcher_listeners() -> None:
    duel = build_duel()

    def custom_requester(*_args: object, **_kwargs: object) -> object:
        return None

    @duel.dispatcher.on(AvailableActions)
    def contribute_custom_action(affair: AvailableActions) -> None:
        affair.actions.append(
            EnterPhase(
                label="Custom draw entry",
                duel=duel,
                phase=duel.state.phase,
                source_phase=duel.state.phase,
                requester=custom_requester,
            )
        )

    actions = duel.available_actions()

    assert any(action.label == "Custom draw entry" for action in actions)
