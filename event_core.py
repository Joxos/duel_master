import threading

class Event:
    pass

class EventManager:
    def __init__(self):
        self._event_classes = {}
        self._subscribers = {}
        self._lock = threading.Lock()

    def register_event(self, event_cls):
        with self._lock:
            self._event_classes[event_cls.__name__] = event_cls
            self._subscribers.setdefault(event_cls, [])

    def subscribe(self, event_cls, callback):
        with self._lock:
            self._subscribers.setdefault(event_cls, []).append(callback)

    def emit(self, event):
        for callback in self._subscribers.get(type(event), []):
            callback(event)

# 单例实例
event_manager = EventManager()
