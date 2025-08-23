from typing import Dict, List, Callable, Type, Deque
from collections import deque
from .log import logger


class Event:
    """Base event class"""

    pass

class Callback:
    def __init__(self, func: Callable[[Event], None], event: Type[Event] | Event, args: Dict = None):
        self.func = func
        self.event = event
        self.args = {}
        if args:
            self.args = args

class EventManager:
    def __init__(self):
        self._callbacks: Dict[Type[Event], List[Callback]] = {}
        self._callstack: Deque[Callback] = deque()

    def subscribe(self, *event_types: Type[Event], _self: Type = None):
        def decorator(func: Callable[[Event], None]):
            for event_type in event_types:
                callback = Callback(func, event_type, args={'self': _self} if _self else {})
                self._callbacks.setdefault(event_type, []).append(callback)
                logger.info(f"Subscribed function {func.__name__} to {event_type.__name__}")
            return func

        return decorator

    def emit(self, event: Event):
        event_type = type(event)
        logger.debug(f"Emitting event: {event_type.__name__}")

        if event_type in self._callbacks:
            logger.info(
                f"Found {len(self._callbacks[event_type])} callbacks for event type: {event_type.__name__}"
            )
            for callback in self._callbacks[event_type]:
                callback_copy = Callback(callback.func, event)
                self._callstack.append(callback_copy)

            # trigger parent class events using callstack
            # for cls in event_type.__mro__[1:]:  # skip self
            #     if cls in self._callbacks and cls != Event:
            #         logger.info(f"Triggering parent class callbacks for: {cls.__name__}")
            #         for callback in self._callbacks[cls]:
            #             callback_copy = Callback(callback.func, event)
            #             self._callstack.append(callback_copy)

            self.process_callstack()

    def process_callstack(self):
        while self._callstack:
            callback = self._callstack.popleft()
            callback, event = callback.func, callback.event
            try:
                logger.debug(
                    f"Processing callstack callback: {callback.__name__}"
                )
                if hasattr(callback, '__self__') and callback.__self__:
                    original_func = callback.__func__
                    bound_instance = callback.__self__

                    original_func(bound_instance, event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"Error in callstack callback {callback.__name__}: {e}")
