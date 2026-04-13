from enum import Enum

from duel_core.models import FrozenModel, MutableModel


class REPRESENTATION(Enum):
    VOID = "void"
    ATTACK = "attack"
    DEFENSE = "defense"


class Card(FrozenModel):
    database_id: int
    name: str
    type: str
    desc: str
    atk: int | None = None
    def_: int | None = None
    level: int | None = None
    race: str | None = None
    attribute: str | None = None


class RuntimeCard(MutableModel):
    runtime_id: int
    card: Card
    representation: REPRESENTATION = REPRESENTATION.VOID
