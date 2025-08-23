from dataclasses import dataclass
from enumerations import PHASE


class Action:
    """Base class for all actions."""

    pass


@dataclass
class NextPhase(Action):
    _from: PHASE
    to: PHASE
