"""Canonical Blue-Eyes White Dragon card definition for the current slice.

This module stores printed facts for the first real runtime card reference.
It must produce a fresh ``Card`` instance per call so multiple copies do not
share object identity during duel progression.
"""

from duel_core.models import Card


BLUE_EYES_WHITE_DRAGON = {
    "id": 89631139,
    "name": "Blue-Eyes White Dragon",
    "type": "Normal Monster",
    "desc": "This legendary dragon is a powerful engine of destruction. Virtually invincible, very few have faced this awesome creature and lived to tell the tale.",
    "atk": 3000,
    "def_": 2500,
    "level": 8,
    "race": "Dragon",
    "attribute": "LIGHT",
}


def blue_eyes_white_dragon_89631139() -> Card:
    return Card(**BLUE_EYES_WHITE_DRAGON)
