from pytest import CaptureFixture, MonkeyPatch

from duel_master import main


def test_cli_renders_observe_and_available_actions(
    monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
) -> None:
    monkeypatch.setattr("builtins.input", lambda _prompt: "")
    assert main() == 0

    output = capsys.readouterr().out
    assert "Current player: Player 1" in output
    assert "Phase: Draw" in output
    assert "Available actions:" in output
    assert "Enter Standby Phase" in output
    assert "End turn" not in output
