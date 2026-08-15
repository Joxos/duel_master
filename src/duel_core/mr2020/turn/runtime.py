class TurnRuntime:
    def __init__(self, *, current_turn_count: int) -> None:
        self.current_turn_count = current_turn_count

    def set_current_turn_count(self, turn_count: int) -> None:
        self.current_turn_count = turn_count
