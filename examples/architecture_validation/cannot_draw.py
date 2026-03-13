from typing import TypedDict


class RuleInteraction(TypedDict):
    action: str
    contributor: str
    outcome: str


class CannotDrawSummary(TypedDict):
    scenario: str
    interactions: list[RuleInteraction]
    invariant: str


def run_example() -> CannotDrawSummary:
    """Show how a cannot-draw effect should interact with the default draw rule.

    Returns:
        Summary of the intended rule collision and resolution.
    """
    return {
        "scenario": "cannot_draw",
        "interactions": [
            {
                "action": "draw_one_card",
                "contributor": "rules.base",
                "outcome": "grant default draw action in Draw Phase",
            },
            {
                "action": "draw_one_card",
                "contributor": "rules.card",
                "outcome": "forbid opponent draw actions while source remains active",
            },
            {
                "action": "can_perform(draw_one_card)",
                "contributor": "substrate.query_reducer",
                "outcome": "resolve to forbidden because forbid outranks grant",
            },
            {
                "action": "legal_actions",
                "contributor": "kernel",
                "outcome": "omit draw action and preserve deterministic replay trace",
            },
        ],
        "invariant": "continuous prohibitions should override default procedure grants through one evaluator",
    }


def main() -> None:
    print(run_example())


if __name__ == "__main__":
    main()
