from __future__ import annotations

import json

from duel_engine.api import run_duel
from duel_engine.replay import Replay
from duel_engine.replay.verify import run_twice_and_compare, verify_replay


def test_verify_replay_accepts_valid_replay(tmp_path):
    replay_path = tmp_path / "valid_replay.json"

    _, replay = run_duel(seed=11, steps=8, policy="deterministic-default")
    replay.save(replay_path)

    replay = Replay.load(replay_path)
    assert verify_replay(replay)


def test_verify_replay_rejects_tampered_replay(tmp_path):
    replay_path = tmp_path / "tampered_replay.json"

    _, replay = run_duel(seed=13, steps=8, policy="deterministic-default")
    replay.save(replay_path)

    payload = json.loads(replay_path.read_text(encoding="utf-8"))
    payload["events"][-1]["state_hash"] = "0" * 64
    replay_path.write_text(json.dumps(payload), encoding="utf-8")

    replay = Replay.load(replay_path)
    assert not verify_replay(replay)


def test_run_twice_and_compare_same_seed_is_deterministic():
    assert run_twice_and_compare(seed=20260311, policy="deterministic-default", steps=12)
