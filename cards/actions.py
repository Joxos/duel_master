from duel.actions import Action
from duel.models import Duel
from duel.constants import SUMMON_TYPE_NORMAL, SUMMON_TYPE_SPECIAL


class CardNameOnePerTurnEffect(Action):
    def __init__(self, effect_action: Action):
        self.effect_action = effect_action

    def available(self, duel: Duel) -> bool:
        for action in duel.history.previous_after(self.effect_action):
            if action == self.effect_action:
                return False
        return True