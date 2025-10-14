class Flag:
    def __init__(self):
        pass


class Condition(Flag):
    def available(self) -> bool:
        return False


class Action(Condition):
    def available(self) -> bool:
        return super().available()
