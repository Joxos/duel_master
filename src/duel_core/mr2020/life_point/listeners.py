from affairon import listen

from duel_core.mr2020.duel.affairs import CompletedAffair, DuelInit
from duel_core.mr2020.life_point.affairs import LpVary

INITIAL_LIFE_POINTS = 8000


@listen(DuelInit)
def assign_initial_life_points(affair: DuelInit) -> None:
    for player in affair.duel.get_players():
        player.life_points = INITIAL_LIFE_POINTS


def apply_lp_vary(affair: LpVary) -> None:
    affair.player.life_points += affair.delta


@listen(LpVary)
def apply_lp_vary_action(affair: LpVary) -> None:
    apply_lp_vary(affair)
    affair.duel.emit(CompletedAffair(duel=affair.duel, affair=affair))
