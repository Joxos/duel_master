from duel_core.mr2020.duel.affairs import DuelAffair, DuelAffairWithRequester


class Forbid(DuelAffair):
    target: DuelAffairWithRequester
    inactive_from_turn: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Forbid):
            return False
        return self.target == other.target
