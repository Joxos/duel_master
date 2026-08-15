from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from affairon import Dispatcher, MutableAffair

from duel_core.mr2020.duel.affairs import AvailableActions, DuelAffairWithRequester, DuelInit
from duel_core.mr2020.duel.bootstrap import compose, rebuild_model_graph
from duel_core.mr2020.duel.providers import ProviderRegistry
from duel_core.mr2020.forbid.runtime import ForbidRuntime
from duel_core.mr2020.phase.models import Phase
from duel_core.mr2020.phase.runtime import PhaseRuntime
from duel_core.mr2020.player.affairs import SetPlayers
from duel_core.mr2020.player.models import Player
from duel_core.mr2020.player.runtime import PlayerRuntime
from duel_core.mr2020.summon.runtime import SummonRuntime
from duel_core.mr2020.turn.runtime import TurnRuntime
from duel_core.mr2020.view.models import PlayerView
from duel_core.mr2020.view.runtime import ViewRuntime

_T = TypeVar("_T")


class Duel:
    dispatcher: Dispatcher
    emit: Callable[[MutableAffair], object]

    def __init__(self, players: tuple[Player, Player], *, starting_player: Player) -> None:
        if len(players) != 2:
            raise ValueError("Duel requires exactly two players")
        if starting_player not in players:
            raise ValueError("Starting player must be one of the duel players")

        self.dispatcher = Dispatcher()
        self.emit = self.dispatcher.emit
        self._providers = ProviderRegistry()

        rebuild_model_graph()
        compose(self)
        self.emit(SetPlayers(duel=self, players=players, starting_player=starting_player))
        self.emit(DuelInit(duel=self))

    def provide(self, provider: _T) -> _T:
        return self._providers.provide(provider)

    def inject(self, key: type[_T]) -> _T:
        return self._providers.inject(key)

    @property
    def state(self) -> Duel:
        return self

    def available_actions(self) -> list[DuelAffairWithRequester]:
        collector = AvailableActions(duel=self)
        self.emit(collector)
        return collector.actions

    def do(self, action: DuelAffairWithRequester) -> None:
        self.inject(ForbidRuntime).do(action)

    def observe(self, player: Player) -> PlayerView:
        return self.inject(ViewRuntime).observe(player)

    def get_players(self) -> tuple[Player, Player]:
        return self.inject(PlayerRuntime).players

    def get_current_player(self) -> Player:
        return self.inject(PlayerRuntime).current_player

    def set_current_player(self, player: Player) -> None:
        self.inject(PlayerRuntime).set_current_player(player)

    def opponent_of(self, player: Player) -> Player:
        return self.inject(PlayerRuntime).opponent_of(player)

    def get_phase(self) -> Phase:
        return self.inject(PhaseRuntime).phase

    def set_phase(self, phase: Phase) -> None:
        self.inject(PhaseRuntime).set_phase(phase)

    def get_current_turn_count(self) -> int:
        return self.inject(TurnRuntime).current_turn_count

    def set_current_turn_count(self, turn_count: int) -> None:
        self.inject(TurnRuntime).set_current_turn_count(turn_count)

    def get_normal_summon_used(self) -> bool:
        return self.inject(SummonRuntime).normal_summon_used

    def set_normal_summon_used(self, used: bool) -> None:
        self.inject(SummonRuntime).set_normal_summon_used(used)


__all__ = ["Duel"]
