from affairon import listen

from duel_core.mr2020.duel.affairs import CompletedAffair, MultiAction


@listen(MultiAction)
def apply_multi_action(affair: MultiAction) -> None:
    for child in affair.children:
        affair.duel.emit(child)
    affair.duel.emit(CompletedAffair(duel=affair.duel, affair=affair))
