from __future__ import annotations

from typing import Any

from duel_engine import __version__
from duel_engine.actions import Action
from duel_engine.api import init_duel, step
from duel_engine.models import GameState
from duel_engine.rng import final_state_hash

from .replay import Replay
from .schema import ReplayData


def _coerce_replay_data(replay: Replay | ReplayData | dict[str, Any]) -> ReplayData:
    if isinstance(replay, Replay):
        return replay.data
    if isinstance(replay, ReplayData):
        return replay
    return ReplayData.from_dict(replay)


def verify_replay(replay: Replay | ReplayData | dict[str, Any]) -> bool:
    data = _coerce_replay_data(replay)
    if data.engine_version != __version__:
        return False

    initial_event = next(
        (item for item in data.events if item.get("type") == "initial_state"),
        None,
    )
    final_event = next(
        (item for item in data.events if item.get("type") == "final_state_hash"),
        None,
    )

    if not isinstance(initial_event, dict) or "state" not in initial_event:
        return False

    state = GameState.from_dict(dict(initial_event["state"]))
    if final_state_hash(state.to_dict()) != data.initial_state_hash:
        return False

    try:
        for action_payload in data.actions:
            action = Action.from_dict(action_payload)
            state = step(state, action)
    except (ValueError, KeyError, TypeError):
        return False

    if not isinstance(final_event, dict) or "state_hash" not in final_event:
        return False

    return final_state_hash(state.to_dict()) == str(final_event["state_hash"])


def run_twice_and_compare(seed: int, policy: str, *, steps: int = 50) -> bool:
    baseline = init_duel(seed=seed)
    first = GameState.from_dict(baseline.to_dict())
    second = GameState.from_dict(baseline.to_dict())

    def select_action(state: GameState) -> Action:
        from duel_engine.actions import ActionType, legal_actions

        actions = legal_actions(state, state.players[(state.turn - 1) % 2].id)
        if not actions:
            raise ValueError("No legal actions available")
        if policy == "deterministic-default":
            return next(
                (a for a in actions if a.action_type == ActionType.PASS_PRIORITY), actions[0]
            )
        raise ValueError(f"Unknown policy: {policy}")

    for _ in range(steps):
        first = step(first, select_action(first))
        second = step(second, select_action(second))

    return final_state_hash(first.to_dict()) == final_state_hash(second.to_dict())
