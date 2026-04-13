from __future__ import annotations

from collections.abc import Callable

from affairon import Dispatcher, MutableAffair

from duel_core.mr2020.duel.affairs import AvailableActions, DuelAffairWithRequester, DuelInit
from duel_core.mr2020.duel.bootstrap import compose, rebuild_model_graph
from duel_core.mr2020.forbid.affairs import Forbid
from duel_core.mr2020.phase.models import Phase
from duel_core.mr2020.player.affairs import SetPlayers
from duel_core.mr2020.player.models import Player
from duel_core.mr2020.view.models import PlayerView


class Duel:
    dispatcher: Dispatcher
    emit: Callable[[MutableAffair], object]

    _players: tuple[Player, Player]
    _current_player: Player
    _current_turn_count: int
    _phase: Phase
    _normal_summon_used: bool
    _active_forbids: list[Forbid]

    get_players: Callable[[], tuple[Player, Player]]
    get_current_player: Callable[[], Player]
    set_current_player: Callable[[Player], None]
    get_current_turn_count: Callable[[], int]
    set_current_turn_count: Callable[[int], None]
    get_phase: Callable[[], Phase]
    set_phase: Callable[[Phase], None]
    get_normal_summon_used: Callable[[], bool]
    set_normal_summon_used: Callable[[bool], None]
    get_active_forbids: Callable[[], list[Forbid]]
    opponent_of: Callable[[Player], Player]
    observe: Callable[[Player], PlayerView]
    do: Callable[[DuelAffairWithRequester], None]

    def __init__(self, players: tuple[Player, Player], *, starting_player: Player) -> None:
        if len(players) != 2:
            raise ValueError("Duel requires exactly two players")
        if starting_player not in players:
            raise ValueError("Starting player must be one of the duel players")

        self.dispatcher = Dispatcher()
        self.emit = self.dispatcher.emit

        rebuild_model_graph()
        compose(self)
        self.emit(SetPlayers(duel=self, players=players, starting_player=starting_player))
        self.emit(DuelInit(duel=self))

    @property
    def state(self) -> Duel:
        return self

    def available_actions(self) -> list[DuelAffairWithRequester]:
        collector = AvailableActions(duel=self)
        self.emit(collector)
        return collector.actions


__all__ = ["Duel"]
