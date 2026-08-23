"""Core state and view models for the current duel slice.

This module holds runtime data shapes, player-facing view shapes, and the
state-owned observe boundary. Rule semantics stay outside these models.
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from duel_core.phase import Phase


class REPRESENTATION(Enum):
    VOID = "void"
    ATTACK = "attack"
    DEFENSE = "defense"


class Card(BaseModel):
    """Printed runtime facts for a single card instance."""

    model_config = ConfigDict(frozen=True)

    id: int
    name: str
    type: str
    desc: str
    atk: int | None = None
    def_: int | None = None
    level: int | None = None
    race: str | None = None
    attribute: str | None = None


class RuntimeCard(BaseModel):
    card: Card
    representation: REPRESENTATION = REPRESENTATION.VOID


class Deck(BaseModel):
    """A draw-capable ordered deck for the current slice."""

    model_config = ConfigDict(validate_assignment=True)

    cards: list[Card]


class Player(BaseModel):
    """Runtime state owned by one duel participant."""

    model_config = ConfigDict(validate_assignment=True)

    label: str
    main_deck: Deck
    extra_deck: list[Card]
    hand: list[RuntimeCard] = Field(default_factory=list)
    monster_zones: list[RuntimeCard | None] = Field(default_factory=lambda: [None])
    graveyard: list[RuntimeCard] = Field(default_factory=list)
    life_points: int = 8000


class DuelState(BaseModel):
    """Kernel-owned runtime state and observe composition boundary."""

    model_config = ConfigDict(validate_assignment=True)

    _VISIBLE_PLAYER_FIELDS = (
        ("label", lambda player: player.label),
        ("monster_zones", lambda player: tuple(player.monster_zones)),
        ("graveyard_size", lambda player: len(player.graveyard)),
        ("life_points", lambda player: player.life_points),
    )
    _PUBLIC_VIEW_FIELDS = (
        ("current_turn", lambda state: state.current_turn),
        ("phase", lambda state: state.phase),
        ("normal_summon_used", lambda state: state.normal_summon_used),
        ("battle_entered", lambda state: state.phase is Phase.BATTLE),
        ("game_over", lambda state: state.game_over),
    )

    players: tuple[Player, Player]
    current_player: Player
    current_turn: int
    phase: Phase
    normal_summon_used: bool = False
    game_over: bool = False
    winner: Player | None = None

    @property
    def opponent(self) -> Player:
        current_index = self.players.index(self.current_player)
        return self.players[(current_index + 1) % len(self.players)]

    def opponent_of(self, player: Player) -> Player:
        if player is self.players[0]:
            return self.players[1]
        if player is self.players[1]:
            return self.players[0]
        raise ValueError("Player must be one of the duel players")

    def _visible_player(self, player: Player) -> "VisiblePlayer":
        data = {field_name: getter(player) for field_name, getter in self._VISIBLE_PLAYER_FIELDS}
        return VisiblePlayer.model_validate(data)

    def _public_view(self) -> "PublicView":
        data = {field_name: getter(self) for field_name, getter in self._PUBLIC_VIEW_FIELDS}
        return PublicView.model_validate(data)

    def observe(self, view: Player) -> "PlayerView":
        opponent = self.opponent_of(view)
        return PlayerView(
            viewer=self._visible_player(view),
            opponent=self._visible_player(opponent),
            current_player=self._visible_player(self.current_player),
            public=self._public_view(),
        )


class PublicView(BaseModel):
    """Public duel facts visible regardless of player perspective."""

    model_config = ConfigDict(frozen=True)

    current_turn: int
    phase: Phase
    normal_summon_used: bool
    battle_entered: bool
    game_over: bool


class VisiblePlayer(BaseModel):
    """Player-facing visible information for one side of the field."""

    model_config = ConfigDict(frozen=True)

    label: str
    monster_zones: tuple[RuntimeCard | None, ...]
    graveyard_size: int
    life_points: int


class PlayerView(BaseModel):
    """Access-controlled player-facing view of the duel state."""

    model_config = ConfigDict(frozen=True)

    viewer: VisiblePlayer
    opponent: VisiblePlayer
    current_player: VisiblePlayer
    public: PublicView
