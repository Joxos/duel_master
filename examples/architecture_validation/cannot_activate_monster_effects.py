from typing import TypedDict


class ActivationInteraction(TypedDict):
    query: str
    contributor: str
    outcome: str


class CannotActivateMonsterEffectsSummary(TypedDict):
    scenario: str
    interactions: list[ActivationInteraction]
    invariant: str


def run_example() -> CannotActivateMonsterEffectsSummary:
    """Show how monster-effect activation locks should resolve.

    Returns:
        Summary of the intended legality interaction.
    """
    return {
        "scenario": "cannot_activate_monster_effects",
        "interactions": [
            {
                "query": "can_activate(monster_effect, opponent)",
                "contributor": "rules.base",
                "outcome": "grant activation if timing, state, and speed requirements are satisfied",
            },
            {
                "query": "can_activate(monster_effect, opponent)",
                "contributor": "rules.card",
                "outcome": "forbid opponent monster-effect activations while effect is active",
            },
            {
                "query": "can_activate(monster_effect, opponent)",
                "contributor": "substrate.query_reducer",
                "outcome": "collapse final answer to false without special-case kernel branching",
            },
            {
                "query": "legal_actions",
                "contributor": "kernel",
                "outcome": "hide monster-effect activation actions while preserving other legal actions",
            },
        ],
        "invariant": "activation legality should be query-driven rather than phase-code special casing",
    }


def main() -> None:
    print(run_example())


if __name__ == "__main__":
    main()
