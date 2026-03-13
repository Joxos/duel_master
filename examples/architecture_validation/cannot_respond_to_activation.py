from dataclasses import dataclass
from typing import TypedDict


@dataclass(frozen=True)
class ResponseDecision:
    activation: str
    contributor: str
    outcome: str


class NoResponseSummary(TypedDict):
    scenario: str
    decisions: list[dict[str, str]]
    invariant: str


def run_example() -> NoResponseSummary:
    """Show how a no-response activation lock should be represented.

    Returns:
        Summary of the intended response-window interaction.
    """
    decisions = [
        ResponseDecision(
            activation="spell_activation_42",
            contributor="rules.base",
            outcome="open response opportunity keyed by activation id",
        ),
        ResponseDecision(
            activation="spell_activation_42",
            contributor="rules.card",
            outcome="forbid response actions tied to this activation id",
        ),
        ResponseDecision(
            activation="respond(spell_activation_42)",
            contributor="substrate.query_reducer",
            outcome="response opportunity resolves to forbidden",
        ),
        ResponseDecision(
            activation="chain_window",
            contributor="kernel",
            outcome="window may still exist, but legal responses list becomes empty",
        ),
    ]
    return {
        "scenario": "cannot_respond_to_this_activation",
        "decisions": [item.__dict__ for item in decisions],
        "invariant": "activation instances must be first-class runtime objects",
    }


def main() -> None:
    print(run_example())


if __name__ == "__main__":
    main()
