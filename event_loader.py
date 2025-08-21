import os
import importlib.util
from event_core import event_manager, Event

MODULES_DIR = os.path.join(os.path.dirname(__file__), "modules")

def load_events_and_subscribers():
    for module_name in os.listdir(MODULES_DIR):
        module_path = os.path.join(MODULES_DIR, module_name)
        events_py = os.path.join(module_path, "events.py")
        if os.path.isdir(module_path) and os.path.isfile(events_py):
            spec = importlib.util.spec_from_file_location(f"{module_name}.events", events_py)
            events_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(events_mod)
            # 注册所有 Event 子类
            for attr in dir(events_mod):
                obj = getattr(events_mod, attr)
                if isinstance(obj, type) and issubclass(obj, Event) and obj is not Event:
                    event_manager.register_event(obj)
            # 注册所有带 _event_subscriptions 的函数
            for attr in dir(events_mod):
                fn = getattr(events_mod, attr)
                if hasattr(fn, "_event_subscriptions"):
                    for event_cls in fn._event_subscriptions:
                        event_manager.subscribe(event_cls, fn)
