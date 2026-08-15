class SummonRuntime:
    def __init__(self, *, normal_summon_used: bool) -> None:
        self.normal_summon_used = normal_summon_used

    def set_normal_summon_used(self, used: bool) -> None:
        self.normal_summon_used = used
