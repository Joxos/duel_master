from duel_core import Deck, Duel, Player


def build_demo_duel() -> Duel:
    return Duel(
        players=(
            Player(main_deck=Deck(cards=[f"p1-{i}" for i in range(10)]), extra_deck=Deck(cards=[])),
            Player(main_deck=Deck(cards=[f"p2-{i}" for i in range(10)]), extra_deck=Deck(cards=[])),
        )
    )


def render(view) -> None:
    print(f"Current player: Player {1 if view.current_player is view.viewer else 2}")
    print(f"Phase: {view.phase.value}")
    print(f"Hand sizes: {view.hand_sizes[0]} / {view.hand_sizes[1]}")


def run_hotseat_demo() -> int:
    duel = build_demo_duel()
    while True:
        render(duel.observe(view=duel.current_player))
        actions = duel.available_actions()
        print("Available actions:")
        if not actions:
            print("  (none)")
            input("")
            return 0

        for index, action in enumerate(actions, start=1):
            print(f"  {index}. {action.label}")

        choice = input("Choose action: ")
        if choice == "":
            return 0
        duel.do(actions[int(choice) - 1])


def main() -> int:
    return run_hotseat_demo()


if __name__ == "__main__":
    raise SystemExit(main())
