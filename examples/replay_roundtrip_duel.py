from duel_engine import Duel
from duel_engine.replay.verify import verify_replay


def run_example() -> dict[str, object]:
    """Run duel generation and verify replay integrity.

    Returns:
        Summary containing final state and replay verification result.
    """
    duel = Duel.create(seed=7)
    final_state = duel.run(steps=8)
    replay = duel.to_replay()
    verified = verify_replay(replay)
    return {
        "final_turn": final_state.turn,
        "final_phase": final_state.phase,
        "verified": verified,
    }


def main() -> None:
    """Execute example and print final summary."""
    print(run_example())


if __name__ == "__main__":
    main()
