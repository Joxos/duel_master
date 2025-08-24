from typing import Dict, List, Callable, Type, Deque
from collections import deque
from .log import logger


class Event:
    """Base event class"""

    pass


class Callback:
    def __init__(
        self,
        func: Callable[[Event], None],
        event: Type[Event] | Event,
        args: Dict = None,
    ):
        self.func = func
        self.event = event
        self.args = {}
        if args:
            self.args = args


class EventManager:
    def __init__(self):
        self._callbacks: Dict[Type[Event], List[Callback]] = {}
        self._callqueue: Deque[Callback] = deque()

    def subscribe(self, *event_types: Type[Event], _self: Type = None):
        def decorator(func: Callable[[Event], None]):
            for event_type in event_types:
                callback = Callback(
                    func, event_type, args={"self": _self} if _self else {}
                )
                self._callbacks.setdefault(event_type, []).append(callback)
                logger.debug(
                    f"Subscribed function {func.__name__} to {event_type.__name__}"
                )
            return func

        return decorator

    def emit(self, event: Event):
        event_type = type(event)
        logger.debug(f"Emitting event: {event_type.__name__}")

        if event_type in self._callbacks:
            logger.debug(
                f"Found {len(self._callbacks[event_type])} callbacks for event type: {event_type.__name__}"
            )
            for callback in self._callbacks[event_type]:
                callback_copy = Callback(callback.func, event)
                self._callqueue.append(callback_copy)

            # trigger parent class events using callqueue
            # for cls in event_type.__mro__[1:]:  # skip self
            #     if cls in self._callbacks and cls != Event:
            #         logger.info(f"Triggering parent class callbacks for: {cls.__name__}")
            #         for callback in self._callbacks[cls]:
            #             callback_copy = Callback(callback.func, event)
            #             self._callqueue.append(callback_copy)

            self.verbose_callqueue()
            self.process_callqueue()

    def process_callqueue(self):
        while self._callqueue:
            callback = self._callqueue.popleft()
            callback, event = callback.func, callback.event
            logger.debug(f"Processing callqueue callback: {callback.__name__}")
            if hasattr(callback, "__self__") and callback.__self__:
                original_func = callback.__func__
                bound_instance = callback.__self__

                @logger.catch
                def wrapper():
                    original_func(bound_instance, event)

                wrapper()
            else:

                @logger.catch
                def wrapper():
                    callback(event)

                wrapper()

    def verbose_callqueue(self):
        for callback in self._callqueue:
            logger.debug(f"Callback in callqueue: {callback.func.__name__}")
