from duel_engine import Duel
from duel_engine.actions import Action, ActionType, legal_actions


def run_example() -> dict[str, object]:
    """Run a minimal single-duel flow through phase progression.

    Returns:
        Summary containing phase progression and final turn ownership.
    """
    duel = Duel.create(seed=1)
    progression = [duel.state.phase]

    scripted_actions = [
        ActionType.DRAW_PHASE,
        ActionType.STANDBY_PHASE,
        ActionType.PASS_PRIORITY,
        ActionType.PASS_PRIORITY,
        ActionType.PASS_PRIORITY,
        ActionType.END_PHASE,
    ]

    for action_type in scripted_actions:
        turn_player_id = duel.turn_player_id()
        legal = {item.action_type for item in legal_actions(duel.state, turn_player_id)}
        if action_type not in legal:
            raise ValueError(f"Action {action_type.value} is not legal at phase {duel.state.phase}")
        duel.apply_action(Action(player_id=turn_player_id, action_type=action_type))
        progression.append(duel.state.phase)

    return {
        "phase_progression": progression,
        "final_turn": duel.state.turn,
        "final_phase": duel.state.phase,
        "priority_player": duel.state.priority_player,
    }


def main() -> None:
    """Execute example and print final summary."""
    print(run_example())


if __name__ == "__main__":
    main()
