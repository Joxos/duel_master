from event_core import Event
from subscribe import subscribe

class MyEvent(Event):
    def __init__(self, msg):
        self.msg = msg

@subscribe(MyEvent)
def on_my_event(event):
    print(f"Received MyEvent: {event.msg}")
