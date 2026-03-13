from typing import TypedDict


class BorrowingSection(TypedDict):
    borrow: list[str]
    use_for: list[str]
    not_directly_keep: list[str]


class BorrowingSummary(TypedDict):
    affairon: BorrowingSection
    moduvent: BorrowingSection
    architectural_judgment: str


def run_example() -> BorrowingSummary:
    """Summarize what is being borrowed from affairon and moduvent.

    Returns:
        Mapping of borrowed ideas, intended use, and cautions.
    """
    return {
        "affairon": {
            "borrow": [
                "typed seam-as-contract",
                "ordered multi-handler collaboration",
                "aggregation mindset",
                "plugin-oriented composition ideas",
            ],
            "use_for": [
                "query/opportunity seam design",
                "ordered rule participation",
                "host-plus-plugin composition model",
            ],
            "not_directly_keep": [
                "dict merge as universal reducer",
                "application-centric CLI/plugin framing",
            ],
        },
        "moduvent": {
            "borrow": [
                "event-class ergonomics",
                "queue/runtime dispatch intuition",
                "simple subscription mental model",
            ],
            "use_for": [
                "deterministic event/procedure runtime",
                "runtime trace ordering",
            ],
            "not_directly_keep": [
                "generic event framework positioning",
                "plugin/module discovery as the core product identity",
            ],
        },
        "architectural_judgment": (
            "Affairon is closer to the seam/reducer side; moduvent is closer to the "
            "event-queue/runtime side. The duel engine should borrow both selectively."
        ),
    }


def main() -> None:
    print(run_example())


if __name__ == "__main__":
    main()
