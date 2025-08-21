import importlib
from loguru import logger
from enumerations import SUMMON_TYPE


IGNORED_EVENTS_LOGGING = []

class Event:
    def __init__(self):
        pass

class OnMonsterSummon(Event):
    def __init__(self, summon_type: SUMMON_TYPE, card):
        self.summon_type = summon_type
        self.monster = card

class OnEffectActivated(Event):
    def __init__(self, card):
        self.card = card

class OnCardMovement(Event):
    def __init__(self, card, _from, to):
        self.card = card
        self._from = _from
        self.to = to


class EventsManager:
    def __init__(self):
        self.events = {}
        self.game_ref = None

    def set_game_ref(self, game_ref):
        self.game_ref = game_ref

    def register(self, event):
        logger.debug(f"Registering event: {event}")
        self.events[event] = []

    def multi_register(self, events):
        for event in events:
            self.register(event)

    def subscribe(self, event, func):
        if isinstance(func, list):
            for f in func:
                logger.debug(f"{event.__name__} -> {f.__name__}")
                self.events[event].append(f)
        else:
            logger.debug(f"{event.__name__} -> {func.__name__}")
            self.events[event].append(func)

    def multi_subscribe(self, subscriptions):
        for event, func in subscriptions.items():
            self.subscribe(event, func)

    def new_event(self, new_event):
        event_type = type(new_event)
        if event_type not in IGNORED_EVENTS_LOGGING:
            logger.debug(f"New event: {new_event.__class__.__name__}")
        for event, func_list in self.events.items():
            if event == event_type:
                for func in func_list:
                    if event_type not in IGNORED_EVENTS_LOGGING:
                        logger.debug(
                            f"Calling function: {func.__name__} with event: {new_event.__class__.__name__}"
                        )
                    func(self.game_ref, new_event, self)
                return

    def import_module(self, name):
        logger.debug(f"Importing module: {name}")
        module = importlib.import_module(name)
        if hasattr(module, "subscriptions"):
            logger.debug(f"Found subscriptions in module: {name}")
            self.multi_subscribe(module.subscriptions)
        if hasattr(module, "registrations"):
            logger.debug(f"Found registrations in module: {name}")
            self.multi_register(module.registrations)

    def import_modules(self, names):
        for name in names:
            self.import_module(name)

    def verbose_subscription_info(self):
        logger.info("Event subscriptions:")
        for event, func_list in self.events.items():
            logger.info(f"{event.__name__}:")
            for func in func_list:
                logger.info(f"  {func.__name__}")
