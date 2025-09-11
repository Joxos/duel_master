from constants import *

class Occasion:
    def __init__(self, code):
        self.code = code

class NormalSummonOccasion(Occasion):
    def __init__(self, monster):
        super().__init__(OCCASION_NORMAL_SUMMON)
        self.monster = monster

class SpecialSummonOccasion(Occasion):
    def __init__(self, monster):
        super().__init__(OCCASION_SPECIAL_SUMMON)
        self.monster = monster