from __future__ import annotations

from typing import Callable, Dict, List, Iterable

from .types import Event, EventType


class EventManager:
    """Simple event manager for yugioh engine.

    - _listeners maps EventType -> list of callables(event: Event) -> None
    - register_listener adds a callback for an event type
    - trigger_event calls all callbacks for a single event and returns them
    - batch_events processes multiple events in order
    """

    def __init__(self) -> None:
        self._listeners: Dict[EventType, List[Callable[[Event], None]]] = {}

    def register_listener(
        self, event_type: EventType, callback: Callable[[Event], None]
    ) -> None:
        """Register a callback to be invoked when events of event_type occur."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def trigger_event(self, event: Event) -> List[Callable[[Event], None]]:
        """Trigger a single event, calling all registered callbacks.

        Returns the list of callbacks that were invoked (in registration order).
        Exceptions raised by callbacks are not suppressed.
        """
        callbacks = list(self._listeners.get(event.event_type, []))
        for cb in callbacks:
            cb(event)
        return callbacks

    def batch_events(self, events: Iterable[Event]) -> List[Event]:
        """Trigger a sequence of events in order and return the list of processed events.

        This method simply calls trigger_event for each event and returns the
        original events as a list to indicate what was processed.
        """
        processed: List[Event] = []
        for evt in events:
            self.trigger_event(evt)
            processed.append(evt)
        return processed


__all__ = ["EventManager"]
