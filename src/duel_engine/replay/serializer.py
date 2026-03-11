from __future__ import annotations

import hashlib
import json

from .schema import ReplayData


def _canonical_json(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def replay_hash(replay: ReplayData) -> str:
    canonical = _canonical_json(replay.to_dict())
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def to_json(replay: ReplayData) -> str:
    return _canonical_json(replay.to_dict())


def from_json(payload: str) -> ReplayData:
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("replay JSON must decode to an object")
    return ReplayData.from_dict(data)
