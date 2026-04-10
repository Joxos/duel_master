"""Core state and view models for the current duel slice.

This module holds runtime data shapes, player-facing view shapes, and the
state-owned observe boundary. Rule semantics stay outside these models.
"""

from enum import Enum
from typing import Self, cast

from pydantic import BaseModel, ConfigDict, Field

from duel_core.phase import Phase


class MutableModel(BaseModel):
    model_config = ConfigDict(validate_assignment=True)


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class REPRESENTATION(Enum):
    VOID = "void"
    ATTACK = "attack"
    DEFENSE = "defense"


class Card(FrozenModel):
    """Printed runtime facts for a single card instance."""

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


class Deck(MutableModel):
    """A draw-capable ordered deck for the current slice."""

    cards: list[Card | RuntimeCard] = Field(default_factory=list)

    def draw(self, num: int) -> list[RuntimeCard]:
        drawn = self.cards[:num]
        del self.cards[:num]
        return cast(list[RuntimeCard], drawn)


class Player(MutableModel):
    """Runtime state owned by one duel participant."""

    label: str
    main_deck: Deck
    extra_deck: Deck = Field(default_factory=Deck)
    hand: list[RuntimeCard] = Field(default_factory=list)
    monster_zones: list[RuntimeCard | None] = Field(default_factory=lambda: [None])
    graveyard: list[RuntimeCard] = Field(default_factory=list)
    life_points: int = 0


class DuelState(MutableModel):
    """Kernel-owned runtime state and observe composition boundary."""

    players: tuple[Player, Player]
    current_player: Player
    current_turn_count: int
    phase: Phase
    normal_summon_used: bool = False

    def opponent_of(self, player: Player) -> Player:
        if player is self.players[0]:
            return self.players[1]
        if player is self.players[1]:
            return self.players[0]
        raise ValueError("Player must be one of the duel players")

    def observe(self, view: Player) -> "PlayerView":
        opponent = self.opponent_of(view)
        return PlayerView.from_state(self, viewer=view, opponent=opponent)


class VisiblePlayer(FrozenModel):
    """Player-facing visible information for one side of the field."""

    label: str
    monster_zones: tuple[RuntimeCard | None, ...]
    graveyard_size: int
    life_points: int

    @classmethod
    def from_player(cls, player: Player) -> Self:
        return cls(
            label=player.label,
            monster_zones=tuple(player.monster_zones),
            graveyard_size=len(player.graveyard),
            life_points=player.life_points,
        )


class PlayerView(FrozenModel):
    viewer: VisiblePlayer
    opponent: VisiblePlayer
    current_player: VisiblePlayer
    current_turn: int
    phase: Phase
    normal_summon_used: bool

    @classmethod
    def from_state(cls, state: DuelState, viewer: Player, opponent: Player) -> Self:
        return cls(
            viewer=VisiblePlayer.from_player(viewer),
            opponent=VisiblePlayer.from_player(opponent),
            current_player=VisiblePlayer.from_player(state.current_player),
            current_turn=state.current_turn_count,
            phase=state.phase,
            normal_summon_used=state.normal_summon_used,
        )
