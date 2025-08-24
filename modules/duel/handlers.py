from .log import logger
from sys import exit
from moduvent import subscribe, event_manager
from enumerations import PHASE
from .models import Duel
from .events import (
    DuelInitialize,
    DuelStart,
    ShowAndGetAction,
    PerformAction,
    NextTurn,
    DuelPreparation,
    DuelEnd,
    EnterPhase,
)


@subscribe(DuelInitialize)
def on_duel_initialize(event: DuelInitialize):
    logger.info(f"Initializing duel between {event.player_1} and {event.player_2}")
    duel = Duel(player_1=event.player_1, player_2=event.player_2)
    event_manager.emit(DuelPreparation(duel))


# DuelPreparation with consequence
@subscribe(DuelPreparation)
def shuffle_deck(event: DuelPreparation):
    event.duel.shuffle_deck(event.duel.player_1)
    event.duel.shuffle_deck(event.duel.player_2)
    logger.success("Both players' decks have been shuffled.")


@subscribe(DuelPreparation)
def initial_draw(event: DuelPreparation):
    event.duel.initial_draw()
    logger.success("Both players have drawn their initial hands.")


@subscribe(DuelPreparation)
def after_duel_preparation(event: DuelPreparation):
    event_manager.emit(DuelStart(event.duel))
    logger.info("DuelPreparation completed, DuelStart event emitted.")


@subscribe(DuelStart)
def console_interaction(event: DuelStart):
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


@subscribe(DuelEnd)
def on_duel_end(event: DuelEnd):
    logger.info(f"Duel ended due to: {event.reason}. Winner: {event.win_player}")
    exit(0)


@subscribe(EnterPhase)
def draw_when_in_draw_phase(event: EnterPhase):
    if event.phase == PHASE.DRAW:
        event.duel.draw(event.duel.current_player)
