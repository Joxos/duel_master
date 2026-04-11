from __future__ import annotations

from typing import TYPE_CHECKING

from affairon.listen import listen

from duel_core.affairs import ExposedUserAction, MoveCard
from duel_core.kernel.appliers import apply_atomic_action
from duel_core.models import REPRESENTATION, Zone
from duel_core.phase import Phase

if TYPE_CHECKING:
    from duel_core.models import Player, RuntimeCard


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
    if affair.duel.state.phase not in (Phase.MAIN_1, Phase.MAIN_2):
        raise ValueError("NormalSummon requires a main phase")
    if affair.duel.state.normal_summon_used:
        raise ValueError("Normal summon already used")
    if affair.card not in affair.player.hand:
        raise ValueError("NormalSummon card must be in hand")
    if affair.card.card.level is None or affair.card.card.level > 4:
        raise ValueError("NormalSummon currently supports level 4 or lower monsters only")
    if affair.to_zone.card is not None:
        raise ValueError("NormalSummon target zone must be empty")

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
