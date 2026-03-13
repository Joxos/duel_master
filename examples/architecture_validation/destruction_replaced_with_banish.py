from typing import TypedDict


class ReplacementInteraction(TypedDict):
    event: str
    contributor: str
    outcome: str


class DestructionReplacementSummary(TypedDict):
    scenario: str
    interactions: list[ReplacementInteraction]
    invariant: str


def run_example() -> DestructionReplacementSummary:
    """Show how destruction replacement should be modeled.

    Returns:
        Summary of the intended replacement interaction.
    """
    return {
        "scenario": "destruction_replaced_with_banish",
        "interactions": [
            {
                "event": "destroy(card_x)",
                "contributor": "kernel",
                "outcome": "prepare primitive destroy event proposal",
            },
            {
                "event": "destroy(card_x)",
                "contributor": "rules.card",
                "outcome": "register replacement that swaps destruction with banishment",
            },
            {
                "event": "replace(destroy(card_x))",
                "contributor": "substrate.event_runtime",
                "outcome": "rewrite pending effect outcome from destroy to banish before commit",
            },
            {
                "event": "banish(card_x)",
                "contributor": "kernel",
                "outcome": "commit banish primitive and emit resulting events",
            },
        ],
        "invariant": "replacement should intercept proposed outcomes before state commit, not patch after the fact",
    }


def main() -> None:
    print(run_example())


if __name__ == "__main__":
    main()
