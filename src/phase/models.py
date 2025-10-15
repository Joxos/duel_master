from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from phase.enum import PHASE
    from player.models import Player


class PhaseWithPlayer:
    def __init__(self, phase: "PHASE", player: "Player"):
        self.phase = phase
        self.player = player

    def __eq__(self, value):
        if not isinstance(value, PhaseWithPlayer):
            return False
        return self.phase == value.phase and self.player == value.player

    def __str__(self):
        return f"Phase: {self.phase}, Player: {self.player}"
