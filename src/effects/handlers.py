from moduvent import emit, subscribe

from duel.events import GetAvailableActivations
from effects.events import Activate, Activation
from utils import choose_and_emit_candidates, cleanup_emit


@subscribe(Activation)
def add_to_chain(event: Activation):
    event.duel.current_chain.append(event)


@subscribe(Activation)
def get_more_activations(event: Activation):
    duel, player = event.duel, event.player
    other_player = duel.other_player(player)
    print("Get more activations...")
    if activations := cleanup_emit(
        emit(GetAvailableActivations(player=other_player, duel=duel))
    ):
        choose_and_emit_candidates(duel, player, activations)


@subscribe(Activate)
def call_effect(event: Activate):
    card, index = event.card, event.index

    # locate the effect
    if card.effects is None:
        return
    effect = card.effects.get(index, None)
    if effect is None:
        return
    effect = effect[1]

    # call the effect
    effect(event)
