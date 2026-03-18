from pytest import CaptureFixture, MonkeyPatch

from duel_master import main


def test_main_returns_zero(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt: "")
    assert main() == 0


def test_main_uses_observe_flow(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt: "")
    assert main() == 0
    captured = capsys.readouterr()
    assert "Current player: Player 1" in captured.out
