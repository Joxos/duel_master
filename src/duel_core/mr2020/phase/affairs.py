from duel_core.mr2020.duel.affairs import DuelAffairWithRequester
from duel_core.mr2020.phase.models import Phase
from duel_core.mr2020.timing.affairs import TimingAction


class EnterPhase(DuelAffairWithRequester, TimingAction):
    phase: Phase
    source_phase: Phase

    def __str__(self) -> str:
        if self.phase is Phase.MAIN_1:
            return "Enter Main Phase 1"
        if self.phase is Phase.MAIN_2:
            return "Enter Main Phase 2"
        return f"Enter {self.phase.value} Phase"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EnterPhase):
            return False
        return (
            super().__eq__(other)
            and self.source_phase is other.source_phase
            and self.phase is other.phase
        )


class ExitPhase(DuelAffairWithRequester, TimingAction):
    phase: Phase


def rebuild_phase_models(namespace: dict[str, object]) -> None:
    for model in (EnterPhase, ExitPhase):
        model.model_rebuild(_types_namespace=namespace)
