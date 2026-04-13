"""Rich-based hotseat CLI for the current duel slice.

The CLI consumes player-facing views from ``Duel.observe`` and renders them for
manual smoke testing of the current architecture-first slice.
"""

from duel_core.cards.blue_eyes_white_dragon_89631139 import blue_eyes_white_dragon_89631139
from duel_core import Duel
from duel_core.mr2020.card.models import Card, RuntimeCard
from duel_core.mr2020.phase.models import Phase
from duel_core.mr2020.player.models import Deck, Player
from duel_core.mr2020.view.models import PlayerView, PublicPlayerView
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def build_demo_duel() -> Duel:
    player_1 = Player(
        label="Player 1",
        main_deck=Deck(
            cards=[
                blue_eyes_white_dragon_89631139(),
                *[
                    Card(
                        database_id=1000 + i,
                        name=f"p1-{i}",
                        type="Normal Monster",
                        desc="Demo monster",
                        atk=1000,
                        def_=1000,
                        level=4,
                        race="Dragon",
                        attribute="LIGHT",
                    )
                    for i in range(10)
                ],
            ]
        ),
        extra_deck=Deck(cards=[]),
    )
    player_2 = Player(
        label="Player 2",
        main_deck=Deck(
            cards=[
                Card(
                    database_id=2000 + i,
                    name=f"p2-{i}",
                    type="Normal Monster",
                    desc="Demo monster",
                    atk=1000,
                    def_=1000,
                    level=4,
                    race="Dragon",
                    attribute="LIGHT",
                )
                for i in range(10)
            ]
        ),
        extra_deck=Deck(cards=[]),
    )
    return Duel(players=(player_1, player_2), starting_player=player_1)


def _format_zone_card(card: RuntimeCard | None) -> str:
    if card is None:
        return "(empty)"
    return card.card.name


def _build_public_player_panel(player: PublicPlayerView, *, border_style: str) -> Panel:
    zone_table = Table(show_header=True, header_style="bold magenta")
    zone_table.add_column("Slot", justify="right", width=4)
    zone_table.add_column("Monster Zone")
    for index, card in enumerate(player.monster_zones, start=1):
        zone_table.add_row(str(index), _format_zone_card(card))
    zone_table.add_row("GY", str(player.graveyard_size))
    zone_table.add_row("LP", str(player.life_points))
    return Panel(zone_table, title=player.label, border_style=border_style)


def _build_private_panel(view: PlayerView) -> Panel:
    hand_table = Table(show_header=True, header_style="bold green")
    hand_table.add_column("#", justify="right", width=3)
    hand_table.add_column("Hand")
    for index, card in enumerate(view.hand, start=1):
        hand_table.add_row(str(index), card.card.name)
    hand_table.add_row("MD", str(view.main_deck_size))
    hand_table.add_row("ED", str(view.extra_deck_size))
    return Panel(hand_table, title=view.player_label, border_style="green")


def _build_status_panel(view: PlayerView) -> Panel:
    status = "\n".join(
        [
            f"Current player: {view.public.current_player_label}",
            f"Viewer: {view.player_label}",
            f"Turn: {view.public.current_turn}",
            f"Phase: {view.public.phase.value}",
            f"Battle entered: {'Yes' if view.public.phase is Phase.BATTLE else 'No'}",
            f"Normal summon used: {'Yes' if view.public.normal_summon_used else 'No'}",
        ]
    )
    return Panel(status, title="Duel Status", border_style="cyan")


def render(view: PlayerView) -> None:
    console.print(_build_status_panel(view))
    console.print(
        Columns(
            [
                _build_private_panel(view),
                _build_public_player_panel(view.public.players[0], border_style="green"),
                _build_public_player_panel(view.public.players[1], border_style="yellow"),
            ]
        )
    )


def run_hotseat_demo() -> int:
    duel = build_demo_duel()
    while True:
        render(duel.observe(duel.state.get_current_player()))
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
