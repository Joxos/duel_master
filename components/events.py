from events import Event
from dataclasses import dataclass
from enumerations import PHASE

@dataclass
class OnEnterPhase(Event):
    _from: PHASE
    to: PHASE
