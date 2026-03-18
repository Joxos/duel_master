from pathlib import Path

from affairon.composer import PluginComposer

from duel_core import Deck, Duel, Player
from duel_core.mr2020 import INITIAL_DRAW_NUM


def build_players() -> tuple[Player, Player]:
    return (
        Player(main_deck=Deck(cards=[f"p1-{i}" for i in range(10)]), extra_deck=Deck(cards=[])),
        Player(main_deck=Deck(cards=[f"p2-{i}" for i in range(10)]), extra_deck=Deck(cards=[])),
    )


def test_constructor_preserves_current_setup_behavior() -> None:
    duel = Duel(players=build_players())

    assert duel.state.players[0].hand == [f"p1-{i}" for i in range(INITIAL_DRAW_NUM)]
    assert duel.state.players[1].hand == [f"p2-{i}" for i in range(INITIAL_DRAW_NUM)]
    assert str(duel.available_actions()[0]) == "Enter Standby Phase"


def test_constructor_composes_plugins_from_pyproject(monkeypatch) -> None:
    called_with: list[Path] = []
    real_compose = PluginComposer.compose_from_pyproject

    def capture_compose(self: PluginComposer, pyproject_path: Path) -> None:
        called_with.append(pyproject_path)
        real_compose(self, pyproject_path)

    monkeypatch.setattr(PluginComposer, "compose_from_pyproject", capture_compose)

    Duel(players=build_players())

    assert called_with == [Path(__file__).resolve().parents[2] / "pyproject.toml"]


def test_setup_cannot_be_run_twice() -> None:
    duel = Duel(players=build_players())

    try:
        duel.setup()
    except ValueError as exc:
        assert "already completed" in str(exc)
    else:
        raise AssertionError("expected second setup call to fail fast")
