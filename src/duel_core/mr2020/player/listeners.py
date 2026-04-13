from affairon import listen

from duel_core.mr2020.player.affairs import SetPlayers
from duel_core.mr2020.player.models import Player


@listen(SetPlayers)
def setup_players(affair: SetPlayers) -> None:
    affair.duel._players = affair.players
    affair.duel._current_player = affair.starting_player


@listen(SetPlayers, after=[setup_players])
def inject_player_helpers(affair: SetPlayers) -> None:
    duel = affair.duel

    def get_players() -> tuple[Player, Player]:
        return duel._players

    def get_current_player() -> Player:
        return duel._current_player

    def set_current_player(player: Player) -> None:
        duel._current_player = player

    def opponent_of(player: Player) -> Player:
        players = duel._players
        if player is players[0]:
            return players[1]
        if player is players[1]:
            return players[0]
        raise ValueError("Player must be one of the duel players")

    duel.get_players = get_players
    duel.get_current_player = get_current_player
    duel.set_current_player = set_current_player
    duel.opponent_of = opponent_of
