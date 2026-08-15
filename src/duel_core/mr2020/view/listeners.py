from affairon import listen

from duel_core.mr2020.duel.affairs import DuelInit
from duel_core.mr2020.view.runtime import ViewRuntime


@listen(DuelInit)
def setup_view_runtime(affair: DuelInit) -> None:
    affair.duel.provide(ViewRuntime(duel=affair.duel))
