from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from loguru import logger


@dataclass
class Event:
    """Base event class"""

    source: Any = None  # Event source


# Global event manager
class EventManager:
    _callbacks: Dict[Event, List[Callable[[Event], None]]] = {}

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
        """Trigger an event"""
        event_type = type(event)
        logger.debug(
            f"Emitting event: {event_type.__name__} from source: {event.source}"
        )
        # Trigger all callbacks for this event type
        if event_type in self._callbacks:
            logger.info(
                f"Found {len(self._callbacks[event_type])} callbacks for event type: {event_type.__name__}"
            )
            for callback in self._callbacks[event_type]:
                try:
                    logger.debug(
                        f"Calling callback: {callback.__name__} for event: {event_type.__name__}"
                    )
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in callback {callback.__name__}: {e}")

        # trigger parent class events
        for cls in event_type.__mro__[1:]:  # skip self
            if cls in self._callbacks and cls != Event:
                logger.info(f"Triggering parent class callbacks for: {cls.__name__}")
                for callback in self._callbacks[cls]:
                    try:
                        logger.debug(
                            f"Calling parent callback: {callback.__name__} for event: {event_type.__name__}"
                        )
                        callback(event)
                    except Exception as e:
                        logger.error(
                            f"Error in parent callback {callback.__name__}: {e}"
                        )


# global event manager instance
event_manager = EventManager()

# alias
subscribe = event_manager.subscribe
