"""Public duel facade and composition root.

This module wires the dispatcher, kernel, rule plugins, and public API surface.
It should expose orchestration methods and leave runtime visibility logic to
``DuelState``.
"""

from affairon import Dispatcher
from affairon.composer import PluginComposer

from duel_core.affairs import (
    Attack,
    AvailableActions,
    CompletedAffair,
    DrawCard,
    Draw,
    DuelAffair,
    DuelInit,
    ExecutableAffair,
    EnterPhase,
    ExitPhase,
    Forbid,
    AdvanceTurn,
    LpVary,
    MultiAffair,
    NormalSummon,
    SendToGraveyard,
)
from duel_core.kernel import Kernel
from duel_core.models import Card, Deck, DuelState, Player, PlayerView, REPRESENTATION, RuntimeCard
from duel_core.phase import Phase
from pathlib import Path

PYPROJECT_PATH = Path(__file__).resolve().parents[2] / "pyproject.toml"


class Duel:
    """Public facade that composes the current duel slice.

    Attributes:
        dispatcher: Affair dispatcher for rule and execution flow.
        kernel: Execution kernel that owns runtime state.
    """

    def __init__(self, players: tuple[Player, Player], *, starting_player: Player) -> None:
        if len(players) != 2:
            raise ValueError("Duel requires exactly two players")
        if starting_player not in players:
            raise ValueError("Starting player must be one of the duel players")

        self._rebuild_affair_models()
        self.dispatcher = Dispatcher()
        self.kernel = Kernel(
            state=DuelState(
                players=players,
                current_player=starting_player,
                current_turn_count=1,
                phase=Phase.DRAW,
            ),
            duel_dispatcher=self.dispatcher,
        )
        self._setup()

    def _setup(self) -> None:
        players = self.state.players
        next_runtime_id = 1

        def to_runtime(card: Card | RuntimeCard) -> RuntimeCard:
            nonlocal next_runtime_id
            source_card = card.card if isinstance(card, RuntimeCard) else card
            source_representation = (
                card.representation if isinstance(card, RuntimeCard) else REPRESENTATION.VOID
            )
            runtime_card = RuntimeCard(
                runtime_id=next_runtime_id,
                card=source_card,
                representation=source_representation,
            )
            next_runtime_id += 1
            return runtime_card

        for player in players:
            player.main_deck = Deck(cards=[to_runtime(card) for card in player.main_deck.cards])
            player.extra_deck = Deck(cards=[to_runtime(card) for card in player.extra_deck.cards])

        composer = PluginComposer(self.dispatcher)
        composer.compose_from_pyproject(PYPROJECT_PATH, profile="duel")
        self.dispatcher.emit(DuelInit(duel=self))

    @staticmethod
    def _rebuild_affair_models() -> None:
        AvailableActions.model_rebuild(
            _types_namespace={"Duel": Duel, "ExecutableAffair": ExecutableAffair}
        )
        CompletedAffair.model_rebuild(
            _types_namespace={
                "Duel": Duel,
                "DuelAffair": DuelAffair,
            }
        )
        Draw.model_rebuild(_types_namespace={"Duel": Duel, "Player": Player})
        DuelInit.model_rebuild(_types_namespace={"Duel": Duel})
        ExecutableAffair.model_rebuild(_types_namespace={"Duel": Duel})
        EnterPhase.model_rebuild(_types_namespace={"Duel": Duel})
        ExitPhase.model_rebuild(_types_namespace={"Duel": Duel})
        Forbid.model_rebuild(_types_namespace={"Duel": Duel})
        MultiAffair.model_rebuild(_types_namespace={"Duel": Duel})
        NormalSummon.model_rebuild(
            _types_namespace={
                "Duel": Duel,
                "Player": Player,
                "Card": Card,
                "RuntimeCard": RuntimeCard,
            }
        )
        Attack.model_rebuild(
            _types_namespace={
                "Duel": Duel,
                "Player": Player,
                "Card": Card,
                "RuntimeCard": RuntimeCard,
            }
        )
        LpVary.model_rebuild(
            _types_namespace={
                "Duel": Duel,
                "Player": Player,
            }
        )
        DrawCard.model_rebuild(
            _types_namespace={
                "Duel": Duel,
                "Player": Player,
                "RuntimeCard": RuntimeCard,
            }
        )
        AdvanceTurn.model_rebuild(
            _types_namespace={
                "Duel": Duel,
                "Player": Player,
            }
        )
        SendToGraveyard.model_rebuild(
            _types_namespace={
                "Duel": Duel,
                "Player": Player,
                "Card": Card,
                "RuntimeCard": RuntimeCard,
            }
        )

    @property
    def state(self) -> DuelState:
        return self.kernel.state

    def observe(self, view: Player) -> PlayerView:
        return self.state.observe(view)

    def available_actions(self) -> list[ExecutableAffair]:
        collector = AvailableActions(duel=self)
        self.dispatcher.emit(collector)
        return collector.actions

    def do(self, action: ExecutableAffair) -> None:
        self.kernel.do(action)
