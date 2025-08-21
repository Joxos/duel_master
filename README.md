# Duel Master Project

## Overview

This project uses an extensible event-driven architecture based on an `EventManager` and a modular system. It is designed for flexibility and easy expansion by adding new modules.

---

## EventManager

The `EventManager` is the core of the event-driven system. It allows you to:

- **Register new event types** by subclassing the `Event` base class.
- **Subscribe callback functions** to specific event types using the `@subscribe` decorator.
- **Emit events** to trigger all registered callbacks for a given event type.

This enables loose coupling between different parts of the system and makes it easy to add new features.

---

## Modules

Modules are self-contained feature packages. Each module is a folder inside the `modules` directory. Modules can define their own events and event handlers.

### Module Structure Best Practices

Each module should have the following structure:

```
modules/
  your_module/
    __init__.py    # Public data
    handlers.py    # Events subscriptions
    events.py      # (Optional) Define Event subclasses and event handlers here
    models.py      # (Optional) Data models for this module
    actions.py     # (Optional) Define bussiness logic here
    ...
```

- **events.py**:  
  - Define all custom events by subclassing `Event`.
  - Use the `@subscribe` decorator to register event handlers.
- **models.py/handlers.py**:  
  - Organize your module's data and logic as needed.

### Example: `events.py`

```python
from event_core import Event
from subscribe import subscribe

class MyCustomEvent(Event):
    def __init__(self, data):
        self.data = data

@subscribe(MyCustomEvent)
def handle_my_event(event):
    print(f"Handled event with data: {event.data}")
```

---

## How to Add a New Module

1. Create a new folder under `modules/`.
2. Add an `events.py` file and define your events and handlers.
3. (Optional) Add other files as needed for your module's logic.

---

## Getting Started

1. Ensure all modules are in the `modules` directory.
2. The system will automatically discover and register events and handlers on startup.
3. Use `event_manager.emit(EventInstance)` to trigger events.

---

## License

MIT License
