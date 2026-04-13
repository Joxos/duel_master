from affairon import listen

from duel_core.mr2020.duel.affairs import DuelInit
from duel_core.mr2020.player.models import Player
from duel_core.mr2020.view.models import PlayerView


@listen(DuelInit)
def attach_observe_impl(affair: DuelInit) -> None:
    duel = affair.duel

    def _observe(view: Player) -> PlayerView:
        if view not in duel.get_players():
            raise ValueError("Player must be one of the duel players")
        return PlayerView.from_duel(duel=duel, viewer=view)

    duel.observe = _observe
