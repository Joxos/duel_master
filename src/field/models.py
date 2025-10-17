from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

from field.enum import ZoneType

if TYPE_CHECKING:
    from cards.models import Card
    from player.models import Player


class Field:
    def __init__(
        self,
        main_deck: List["Card"],
        extra_deck: List["Card"],
        hands: Optional[List["Card"]],
    ):
        self.main_deck = main_deck
        self.extra_deck = extra_deck
        self.hands = hands or []
        self.main_monster_zone_1: Optional["Card"] = None
        self.main_monster_zone_2: Optional["Card"] = None
        self.main_monster_zone_3: Optional["Card"] = None
        self.main_monster_zone_4: Optional["Card"] = None
        self.main_monster_zone_5: Optional["Card"] = None
        self.main_monster_zones: List[Optional["Card"]] = [
            self.main_monster_zone_1,
            self.main_monster_zone_2,
            self.main_monster_zone_3,
            self.main_monster_zone_4,
            self.main_monster_zone_5,
        ]
        self.spell_trap_zone_1: Optional["Card"] = None
        self.spell_trap_zone_2: Optional["Card"] = None
        self.spell_trap_zone_3: Optional["Card"] = None
        self.spell_trap_zone_4: Optional["Card"] = None
        self.spell_trap_zone_5: Optional["Card"] = None
        self.spell_trap_zones: List[Optional["Card"]] = [
            self.spell_trap_zone_1,
            self.spell_trap_zone_2,
            self.spell_trap_zone_3,
            self.spell_trap_zone_4,
            self.spell_trap_zone_5,
        ]
        self.extra_monster_zone_1: Optional["Card"] = None
        self.extra_monster_zone_2: Optional["Card"] = None
        self.extra_monster_zones: List[Optional["Card"]] = [
            self.extra_monster_zone_1,
            self.extra_monster_zone_2,
        ]
        self.field_zone: Optional["Card"] = None
        self.graveyard: List["Card"] = []
        self.banished: List["Card"] = []

        self.convert = {
            ZoneType.MAIN_MONSTER_ZONE: self.main_monster_zones,
            ZoneType.FIELD_ZONE: self.field_zone,
            ZoneType.SPELL_TRAP_ZONE: self.spell_trap_zones,
            ZoneType.EXTRA_MONSTER_ZONE: self.extra_monster_zones,
            ZoneType.HAND: self.hands,
            ZoneType.MAIN_DECK: self.main_deck,
            ZoneType.EXTRA_DECK: self.extra_deck,
            ZoneType.GRAVEYARD: self.graveyard,
            ZoneType.BANISHED: self.banished,
        }


@dataclass
class Location:
    player: "Player"
    zone: "ZoneType"
