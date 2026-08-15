from affairon import listen

from duel_core.mr2020.player.affairs import SetPlayers
from duel_core.mr2020.player.runtime import PlayerRuntime


@listen(SetPlayers)
def setup_players(affair: SetPlayers) -> None:
    affair.duel.provide(PlayerRuntime(affair.players, current_player=affair.starting_player))
