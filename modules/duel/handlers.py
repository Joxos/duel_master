from .log import logger
from moduvent import subscribe, event_manager
from .models import Duel
from .events import (
    DuelInitialize,
    DuelStart,
    ShowAndGetAction,
    PerformAction,
    NextTurn,
)


@subscribe(DuelInitialize)
def on_duel_initialize(event: DuelInitialize):
    logger.info(f"Initializing duel between {event.player_1} and {event.player_2}")
    duel = Duel(player_1=event.player_1, player_2=event.player_2)
    event_manager.emit(DuelStart(duel))


@subscribe(DuelStart)
def on_duel_start(event: DuelStart):
    logger.info("Duel started.")
    event_manager.emit(ShowAndGetAction(event.duel))


@subscribe(NextTurn)
def on_turn_chance(event: NextTurn):
    event.duel.next_turn()
    event.duel.verbose_state()


@subscribe(ShowAndGetAction)
def on_show_and_get_action(event: ShowAndGetAction):
    event.duel.show_and_get_action()


@subscribe(PerformAction)
def on_perform_action(event: PerformAction):
    logger.info(f"Performing action: {event.action}")
    event.duel.perform_action(event.action)
    logger.success("Action performed successfully.")
    event_manager.emit(ShowAndGetAction(event.duel))
