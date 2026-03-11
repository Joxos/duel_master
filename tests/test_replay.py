from duel_engine.replay import REPLAY_SCHEMA_VERSION, Replay, ReplayData


def _sample_replay_data() -> ReplayData:
    return ReplayData(
        engine_version="0.0.1",
        ruleset_id="MR2020",
        seed=20260311,
        initial_state_hash="a" * 64,
        actions=[
            {"type": "DRAW", "player": "p1", "card": "hidden_1"},
            {"type": "SET", "player": "p1", "zone": "SZ_0", "card": "hidden_2"},
        ],
        choices=[
            {"player": "p1", "request": "priority", "choice": "pass"},
            {"player": "p2", "request": "response", "choice": "pass"},
        ],
        events=[{"event": "turn_start", "turn": 1, "player": "p1"}],
    )


def test_replay_roundtrip_preserves_data():
    replay = Replay(data=_sample_replay_data())

    payload = replay.to_json()
    restored = Replay.from_json(payload)

    assert restored.data == replay.data
    assert restored.data.to_dict()["schema_version"] == REPLAY_SCHEMA_VERSION


def test_same_replay_produces_same_hash():
    replay_one = Replay(data=_sample_replay_data())
    replay_two = Replay.from_json(replay_one.to_json())

    assert replay_one.replay_hash() == replay_two.replay_hash()


def test_replay_save_load_and_verify(tmp_path):
    replay = Replay(data=_sample_replay_data())
    replay_file = tmp_path / "replay.json"
    expected_hash = replay.replay_hash()

    replay.save(replay_file)
    loaded = Replay.load(replay_file)

    assert loaded.data == replay.data
    assert loaded.verify(expected_hash)
