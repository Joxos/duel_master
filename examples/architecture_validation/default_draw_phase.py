from dataclasses import dataclass
from typing import TypedDict


@dataclass(frozen=True)
class ScenarioObservation:
    action: str
    source: str
    result: str


class DefaultDrawPhaseSummary(TypedDict):
    scenario: str
    observations: list[dict[str, str]]
    invariant: str


def run_example() -> DefaultDrawPhaseSummary:
    """Show how default Draw Phase would split across layers.

    Returns:
        Summary of the intended cross-layer collaboration.
    """
    observations = [
        ScenarioObservation(
            action="enter_draw_phase",
            source="rules",
            result="MR2020 grants the Draw Phase opportunity",
        ),
        ScenarioObservation(
            action="perform_default_draw",
            source="rules",
            result="default draw is expressed as a rule object, not hardcoded phase text",
        ),
        ScenarioObservation(
            action="draw_one_card",
            source="kernel",
            result="kernel commits the primitive draw operation",
        ),
        ScenarioObservation(
            action="card_moved_to_hand",
            source="substrate",
            result="event/runtime layer records the resulting causal event",
        ),
    ]
    return {
        "scenario": "default_draw_phase",
        "observations": [item.__dict__ for item in observations],
        "invariant": "base procedure should still be representable as ordinary rule objects",
    }


def main() -> None:
    print(run_example())


if __name__ == "__main__":
    main()
