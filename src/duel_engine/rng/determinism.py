from __future__ import annotations

import hashlib
import json
from typing import Any, Sequence

from .engine import RNG


def _stable_hash(payload: Any) -> str:
    normalized = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def deterministic_shuffle_hash(seed: int, values: Sequence[Any]) -> str:
    rng = RNG(seed)
    shuffled = list(values)
    rng.shuffle(shuffled)
    return _stable_hash(shuffled)


def replay_hash(seed: int, actions: Sequence[Any]) -> str:
    return _stable_hash({"seed": seed, "actions": list(actions)})


def final_state_hash(state_payload: Any) -> str:
    return _stable_hash(state_payload)
