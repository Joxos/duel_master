from dataclasses import dataclass
from typing import TypedDict


@dataclass(frozen=True)
class LayerDecision:
    action: str
    contributor: str
    decision: str


class BattleLockSummary(TypedDict):
    scenario: str
    decisions: list[dict[str, str]]
    invariant: str


def run_example() -> BattleLockSummary:
    """Show how a temporary battle-phase lock should be resolved.

    Returns:
        Summary of the intended rule interaction.
    """
    decisions = [
        LayerDecision(
            action="enter_battle_phase",
            contributor="rules.base",
            decision="grant opportunity to enter Battle Phase",
        ),
        LayerDecision(
            action="enter_battle_phase",
            contributor="rules.card",
            decision="forbid opponent from entering Battle Phase this turn",
        ),
        LayerDecision(
            action="can_perform(enter_battle_phase)",
            contributor="substrate.query_reducer",
            decision="resolve grant+forbid to forbidden",
        ),
        LayerDecision(
            action="legal_actions",
            contributor="kernel",
            decision="do not surface Enter Battle Phase action to the user",
        ),
    ]
    return {
        "scenario": "cannot_enter_battle_phase_this_turn",
        "decisions": [item.__dict__ for item in decisions],
        "invariant": "base rules and card rules must collide through one rule evaluator",
    }


def main() -> None:
    print(run_example())


if __name__ == "__main__":
    main()
