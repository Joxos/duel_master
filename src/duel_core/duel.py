from pathlib import Path

from affairon import Dispatcher
from affairon.composer import PluginComposer

from duel_core.affairs import (
    AvailableActions,
    CompletedAffair,
    Draw,
    DuelInit,
    ExecutableAffair,
    EnterPhase,
    ExecutionRequest,
    ExitPhase,
    Forbid,
    MultiAffair,
    TurnCleanup,
)
from duel_core.kernel import Kernel
from duel_core.models import DuelView, Player, DuelState
from duel_core.phase import Phase

PYPROJECT_PATH = Path(__file__).resolve().parents[2] / "pyproject.toml"


class Duel:
    def __init__(self, players: tuple[Player, Player]) -> None:
        if len(players) != 2:
            raise ValueError("Duel requires exactly two players")

        self._rebuild_affair_models()
        self._setup_done = False
        self.dispatcher = Dispatcher()
        self.kernel = Kernel(
            DuelState(
                players=players,
                current_player=players[0],
                current_turn=1,
                phase=Phase.DRAW,
            )
        )
        self.kernel.register(self.dispatcher)
        self.setup()

    @staticmethod
    def _rebuild_affair_models() -> None:
        AvailableActions.model_rebuild(
            _types_namespace={"Duel": Duel, "ExecutableAffair": ExecutableAffair}
        )
        CompletedAffair.model_rebuild(
            _types_namespace={"Duel": Duel, "ExecutableAffair": ExecutableAffair}
        )
        Draw.model_rebuild(_types_namespace={"Duel": Duel, "Player": Player})
        DuelInit.model_rebuild(_types_namespace={"Duel": Duel})
        ExecutableAffair.model_rebuild(_types_namespace={"Duel": Duel})
        EnterPhase.model_rebuild(_types_namespace={"Duel": Duel})
        ExecutionRequest.model_rebuild(
            _types_namespace={"Duel": Duel, "ExecutableAffair": ExecutableAffair}
        )
        ExitPhase.model_rebuild(_types_namespace={"Duel": Duel})
        TurnCleanup.model_rebuild(_types_namespace={"Duel": Duel})
        Forbid.model_rebuild(_types_namespace={"Duel": Duel})
        MultiAffair.model_rebuild(_types_namespace={"Duel": Duel})

    @property
    def players(self) -> tuple[Player, Player]:
        return self.kernel.state.players

    @property
    def current_player(self) -> Player:
        return self.kernel.state.current_player

    @property
    def current_turn(self) -> int:
        return self.kernel.state.current_turn

    @property
    def phase(self) -> Phase:
        return self.kernel.state.phase

    def emit(self, affair) -> None:
        self.dispatcher.emit(affair)

    def setup(self) -> None:
        if self._setup_done:
            raise ValueError("Duel setup already completed")

        composer = PluginComposer(self.dispatcher)
        composer.compose_from_pyproject(PYPROJECT_PATH)
        self.emit(DuelInit(duel=self))
        self._setup_done = True

    def observe(self, view: Player) -> DuelView:
        return DuelView(
            viewer=view,
            current_player=self.current_player,
            current_turn=self.current_turn,
            phase=self.phase,
            hand_sizes=(len(self.players[0].hand), len(self.players[1].hand)),
            deck_sizes=(len(self.players[0].main_deck.cards), len(self.players[1].main_deck.cards)),
        )

    def available_actions(self) -> list[ExecutableAffair]:
        collector = AvailableActions(duel=self)
        self.emit(collector)
        return collector.actions

    def do(self, action: ExecutableAffair) -> None:
        if action not in self.available_actions():
            raise ValueError("Unknown action")
        self.emit(ExecutionRequest(duel=self, affair=action))
