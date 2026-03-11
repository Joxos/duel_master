from duel_engine.events import EventType, Event, EventManager, SEGOC


def test_eventtype_values():
    # ensure enum members exist and are unique
    members = set(m.name for m in EventType)
    assert "SUMMONED" in members
    assert "DESTROYED" in members
    assert len(members) == len(list(EventType))


def test_event_dataclass_creation():
    e = Event(
        event_type=EventType.SUMMONED,
        source_card_id="C1",
        target_card_id=None,
        player_id="P1",
        timestamp=123,
    )
    assert e.event_type == EventType.SUMMONED
    assert e.source_card_id == "C1"
    assert e.target_card_id is None
    assert e.player_id == "P1"
    assert e.timestamp == 123


def test_event_manager_register_and_trigger():
    mgr = EventManager()
    seen: list[Event] = []

    def cb(evt: Event) -> None:
        seen.append(evt)

    mgr.register_listener(EventType.DESTROYED, cb)
    ev = Event(
        event_type=EventType.DESTROYED,
        source_card_id="C2",
        target_card_id=None,
        player_id="P2",
        timestamp=1,
    )
    callbacks = mgr.trigger_event(ev)
    assert callbacks and callbacks[0] is cb
    assert seen == [ev]


def test_event_manager_batch_events():
    mgr = EventManager()
    seen: list[Event] = []

    def cb(evt: Event) -> None:
        seen.append(evt)

    mgr.register_listener(EventType.DAMAGED, cb)
    events = [
        Event(
            event_type=EventType.DAMAGED,
            source_card_id="S1",
            target_card_id=None,
            player_id="A",
            timestamp=1,
        ),
        Event(
            event_type=EventType.DAMAGED,
            source_card_id="S2",
            target_card_id=None,
            player_id="B",
            timestamp=2,
        ),
    ]
    processed = mgr.batch_events(events)
    assert processed == events
    assert seen == events


def test_segoc_mandatory_first_and_then_by_turn_player():
    # effects may be dict-like or object-like
    class Eff:
        def __init__(self, owner=None, mandatory=False, name=""):
            self.owner = owner
            self.mandatory = mandatory
            self.name = name

        def __repr__(self):
            return f"Eff({self.name})"

    e1 = {"owner": "P1", "mandatory": True, "name": "m1"}
    e2 = {"owner": "P2", "mandatory": False, "name": "o1"}
    e3 = Eff(owner="P1", mandatory=False, name="o2")
    e4 = Eff(owner="P2", mandatory=True, name="m2")

    # mandatory first preserves relative order among same class
    effects = [e1, e2, e3, e4]
    mand_first = SEGOC.mandatory_first(effects)
    # mandatory ones should be first and keep original relative order (e1 then e4)
    assert mand_first[0] is e1
    assert mand_first[1] is e4

    # then_by_turn_player should place P1 effects first
    by_turn = SEGOC.then_by_turn_player(effects, "P1")
    # P1 effects: e1 and e3 (in that relative order)
    assert by_turn[0] is e1
    assert by_turn[1] is e3
