from typing import Dict, List, Callable, Type, Deque
from collections import deque
from .log import logger


class Event:
    """Base event class"""

    pass


class EventManager:
    def __init__(self):
        self._callbacks: Dict[Type[Event], List[Callable[[Event], None]]] = {}
        self._callstack: Deque[Callable[[Event], None]] = deque()

    def subscribe(self, event_type: Event):
        """Subscribe a function to a specific event type"""

        def decorator(func):
            if event_type not in self._callbacks:
                logger.debug(
                    f"First subscription for event type: {event_type.__name__}"
                )
                self._callbacks[event_type] = []
            logger.info(
                f"Subscribing {func.__name__} to event type: {event_type.__name__}"
            )
            self._callbacks[event_type].append(func)
            return func

        return decorator

    def emit(self, event: Event):
        event_type = type(event)
        logger.debug(f"Emitting event: {event_type.__name__}")

        if event_type in self._callbacks:
            logger.info(
                f"Found {len(self._callbacks[event_type])} callbacks for event type: {event_type.__name__}"
            )
            self._callstack.extend(self._callbacks[event_type])
            self.process_callstack(event)

        # trigger parent class events using callstack
        for cls in event_type.__mro__[1:]:  # skip self
            if cls in self._callbacks and cls != Event:
                logger.info(f"Triggering parent class callbacks for: {cls.__name__}")
                self._callstack.extend(self._callbacks[cls])
        self.process_callstack(event)

    def process_callstack(self, event: Event):
        while self._callstack:
            callback = self._callstack.popleft()
            try:
                logger.debug(
                    f"Processing callstack callback: {callback.__name__} for event: {type(event).__name__}"
                )
                callback(event)
            except Exception as e:
                logger.error(f"Error in callstack callback {callback.__name__}: {e}")
