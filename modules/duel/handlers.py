from loguru import logger
from events import subscribe, Event, event_manager
from modules.duel import Player, Duel
from modules.duel.actions import show_actions

duel = None


class DuelInitialize(Event):
    def __init__(self, player_1: Player, player_2: Player):
        super().__init__()
        self.player_1 = player_1
        self.player_2 = player_2


class DuelStart(Event):
    def __init__(self):
        super().__init__()


class ShowAndGetAction(Event):
    def __init__(self):
        super().__init__()


class PerformAction(Event):
    def __init__(self, action):
        super().__init__()
        self.action = action


class TurnChance(Event):
    def __init__(self, player: Player):
        super().__init__()
        self.player = player


@subscribe(DuelInitialize)
def on_duel_initialize(event: DuelInitialize):
    global duel
    logger.info(f"Initializing duel between {event.player_1} and {event.player_2}")
    duel = Duel(player_1=event.player_1, player_2=event.player_2)
    event_manager.emit(DuelStart())
    logger.debug("DuelStart event emitted.")


@subscribe(DuelStart)
def on_duel_start(event: DuelStart):
    logger.info("Duel started.")
    event_manager.emit(ShowAndGetAction())
    logger.debug("ShowAndGetAction event emitted.")


@subscribe(ShowAndGetAction)
def on_show_and_get_action(event: ShowAndGetAction):
    global duel
    if duel:
        logger.info("Prompting player for action.")
        action = None
        while not action:
            actions = duel.available_actions()
            show_actions(actions)
            try:
                choice = int(input("Choose an action: "))
                action = actions[choice]
                logger.success(f"Player selected action: {action}")
            except (ValueError, IndexError):
                logger.warning("Invalid action choice entered.")
                print("Invalid choice. Please try again.")
        event_manager.emit(PerformAction(action))
        logger.debug("PerformAction event emitted.")


@subscribe(PerformAction)
def on_perform_action(event: PerformAction):
    global duel
    if duel:
        logger.info(f"Performing action: {event.action}")
        try:
            duel.perform_action(event.action)
            logger.success("Action performed successfully.")
        except Exception as e:
            logger.error(f"Error performing action: {e}")
        event_manager.emit(ShowAndGetAction())


@subscribe(TurnChance)
def on_turn_chance(event: TurnChance):
    logger.info(f"It's {event.player}'s turn.")
