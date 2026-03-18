from duel_core import Deck, Duel, Player
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def build_demo_duel() -> Duel:
    return Duel(
        players=(
            Player(main_deck=Deck(cards=[f"p1-{i}" for i in range(10)]), extra_deck=Deck(cards=[])),
            Player(main_deck=Deck(cards=[f"p2-{i}" for i in range(10)]), extra_deck=Deck(cards=[])),
        )
    )


def render(duel: Duel, view) -> None:
    current_index = duel.state.players.index(view.public.current_player)
    console.print(
        Panel(
            f"Current player: Player {current_index + 1}\nPhase: {view.public.phase.value}",
            title="Duel Status",
            border_style="cyan",
        )
    )


def run_hotseat_demo() -> int:
    duel = build_demo_duel()
    while True:
        render(duel, duel.observe(view=duel.state.current_player))
        actions = duel.available_actions()
        if not actions:
            console.print(Panel("(none)", title="Available actions", border_style="yellow"))
            input("")
            return 0

        action_table = Table(title="Available actions")
        action_table.add_column("#", justify="right", width=3)
        action_table.add_column("Action")
        for index, action in enumerate(actions, start=1):
            action_table.add_row(str(index), str(action))
        console.print(action_table)

        choice = input("Choose action: ")
        if choice == "":
            return 0
        duel.do(actions[int(choice) - 1])


def main() -> int:
    return run_hotseat_demo()


if __name__ == "__main__":
    raise SystemExit(main())
