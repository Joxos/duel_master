from typing import TypedDict


class ModifierInteraction(TypedDict):
    query: str
    contributor: str
    outcome: str


class ContinuousAtkModifierSummary(TypedDict):
    scenario: str
    interactions: list[ModifierInteraction]
    invariant: str


def run_example() -> ContinuousAtkModifierSummary:
    """Show how continuous ATK modifiers should be query-time effects.

    Returns:
        Summary of the intended modifier interaction.
    """
    return {
        "scenario": "continuous_atk_modifier",
        "interactions": [
            {
                "query": "current_atk(card_x)",
                "contributor": "kernel",
                "outcome": "provide base ATK from canonical state only",
            },
            {
                "query": "current_atk(card_x)",
                "contributor": "rules.card",
                "outcome": "register continuous +500 ATK modifier while source remains applicable",
            },
            {
                "query": "current_atk(card_x)",
                "contributor": "substrate.query_reducer",
                "outcome": "apply active modifier stack during query evaluation",
            },
            {
                "query": "state_snapshot",
                "contributor": "kernel",
                "outcome": "expose derived ATK in views without mutating base stat storage",
            },
        ],
        "invariant": "continuous modifiers should derive values at query time instead of rewriting base state",
    }


def main() -> None:
    print(run_example())


if __name__ == "__main__":
    main()
