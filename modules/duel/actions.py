from dataclasses import dataclass
from enumerations import PHASE
from .log import logger
from .models import Duel
from moduvent import event_manager
from .events import TurnChance


class Action:
    """Base class for all actions."""

    pass


@dataclass
class NextPhase(Action):
    _from: PHASE
    to: PHASE


def show_actions(actions: list[Action]):
    print("Available actions:")
    for index, action in enumerate(actions):
        if isinstance(action, NextPhase):
            print(f"{index}: Change phase from {action._from} to {action.to}")


def available_phases(duel: Duel):
    phases = PHASE.CONSEQUENCE[duel.current_phase]
    logger.debug(f"Available phases from {duel.current_phase}: {phases}")
    return phases


def next_phase(duel: Duel, phase: PHASE):
    if phase in PHASE.CONSEQUENCE[duel.current_phase]:
        logger.info(f"Phase changing from {duel.current_phase} to {phase}")
        duel.current_phase = phase
    else:
        logger.error(
            f"Incorrect phase change attempted: from {duel.current_phase} to {phase}"
        )
        raise RuntimeError(
            f"Incorrect phase change: from {duel.current_phase} to {phase}."
        )


def available_actions(duel: Duel):
    actions = [
        NextPhase(_from=duel.current_phase, to=phase)
        for phase in PHASE.CONSEQUENCE[duel.current_phase]
    ]
    logger.debug(f"Available actions in phase {duel.current_phase}: {actions}")
    return actions


def perform_action(duel: Duel, action: Action):
    if isinstance(action, NextPhase):
        logger.info(f"Performing action: NextPhase from {action._from} to {action.to}")
        if action.to == PHASE.DRAW:
            event_manager.emit(TurnChance(duel.current_player))
        next_phase(duel, action.to)
    else:
        logger.warning(f"Action {action} is not implemented.")
        raise NotImplementedError(f"Action {action} is not implemented.")
