from dataclasses import dataclass
from enumerations import PHASE

@dataclass
class NextPhase:
    _from: PHASE
    to: PHASE

def show_actions(actions):
    print("Available actions:")
    for index, action in enumerate(actions):
        if isinstance(action, NextPhase):
            print(f"{index}: Change phase from {action._from} to {action.to}")