from __future__ import annotations

from typing import TYPE_CHECKING

from affairon.listen import listen

from duel_core.affairs import ExposedUserAction, MoveCard
from duel_core.kernel.appliers import apply_atomic_action
from duel_core.mr2020.models import REPRESENTATION, Zone

if TYPE_CHECKING:
    from duel_core.mr2020.models import Player, RuntimeCard


class NormalSummon(ExposedUserAction):
    player: Player
    card: RuntimeCard
    to_zone: Zone
    from_representation: REPRESENTATION
    to_representation: REPRESENTATION
    normal_summon_used_from: bool
    normal_summon_used_to: bool

    def __str__(self) -> str:
        return f"Normal Summon {self.card.card.name}"

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return False
        assert isinstance(other, NormalSummon)
        return (
            super().__eq__(other)
            and self.player is other.player
            and self.card == other.card
            and self.to_zone is other.to_zone
        )


@listen(NormalSummon)
def plan_normal_summon(affair: NormalSummon) -> None:
    apply_atomic_action(
        MoveCard(
            duel=affair.duel,
            player=affair.player,
            card=affair.card,
            from_area="hand",
            to_area="monster_zone",
            to_zone=affair.to_zone,
            from_representation=affair.from_representation,
            to_representation=affair.to_representation,
        )
    )
    affair.duel.kernel.state.normal_summon_used = affair.normal_summon_used_to
    affair.duel.kernel.complete(affair)
