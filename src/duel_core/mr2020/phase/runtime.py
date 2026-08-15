from duel_core.mr2020.phase.models import Phase


class PhaseRuntime:
    def __init__(self, *, phase: Phase) -> None:
        self.phase = phase

    def set_phase(self, phase: Phase) -> None:
        self.phase = phase
