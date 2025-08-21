from dataclasses import dataclass
from enumerations import PHASE

@dataclass
class WhenEnterPhase:
    _from: PHASE
    to: PHASE
