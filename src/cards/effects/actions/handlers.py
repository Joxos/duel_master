from cards.effects.actions.events import SetPhase
from moduvent import subscribe
from duel.utils import show_duel_info

@subscribe(SetPhase)
def set_phase(event: SetPhase):
    duel, phase = event.duel, event.phase
    duel.phase = phase
    show_duel_info(duel)
