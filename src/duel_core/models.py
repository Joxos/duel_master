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


class Zone(MutableModel):
    card: RuntimeCard | None = None


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
    monster_zones: list[Zone] = Field(default_factory=lambda: [Zone()])
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
        if view not in self.players:
            raise ValueError("Player must be one of the duel players")
        return PlayerView.from_state(self, viewer=view)


class PublicPlayerView(FrozenModel):
    label: str
    monster_zones: tuple[RuntimeCard | None, ...]
    graveyard_size: int
    life_points: int

    @classmethod
    def from_player(cls, player: Player) -> Self:
        return cls(
            label=player.label,
            monster_zones=tuple(zone.card for zone in player.monster_zones),
            graveyard_size=len(player.graveyard),
            life_points=player.life_points,
        )


class PublicView(FrozenModel):
    current_player_label: str
    current_turn: int
    phase: Phase
    normal_summon_used: bool
    players: tuple[PublicPlayerView, PublicPlayerView]

    @classmethod
    def from_state(cls, state: DuelState) -> Self:
        public_players = tuple(PublicPlayerView.from_player(player) for player in state.players)
        return cls(
            current_player_label=state.current_player.label,
            current_turn=state.current_turn_count,
            phase=state.phase,
            normal_summon_used=state.normal_summon_used,
            players=cast(tuple[PublicPlayerView, PublicPlayerView], public_players),
        )


class PlayerView(FrozenModel):
    player_label: str
    hand: tuple[RuntimeCard, ...]
    main_deck_size: int
    extra_deck_size: int
    public: PublicView

    @classmethod
    def from_state(cls, state: DuelState, viewer: Player) -> Self:
        return cls(
            player_label=viewer.label,
            hand=tuple(viewer.hand),
            main_deck_size=len(viewer.main_deck.cards),
            extra_deck_size=len(viewer.extra_deck.cards),
            public=PublicView.from_state(state),
        )
