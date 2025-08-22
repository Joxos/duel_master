from .event_manager import EventManager, Event
from .module_loader import ModuleLoader

event_manager = EventManager()
module_loader = ModuleLoader(event_manager=event_manager)
discover_modules = module_loader.discover_modules
subscribe = event_manager.subscribe
emit = event_manager.emit

__all__ = [EventManager, Event, ModuleLoader, discover_modules, subscribe, emit]
