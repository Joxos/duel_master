"""Core state and view models for the current duel slice.

This module holds runtime data shapes, player-facing view shapes, and the
state-owned observe boundary. Rule semantics stay outside these models.
"""

from collections.abc import Callable
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from duel_core.phase import Phase


class Card(BaseModel):
    """Printed runtime facts for a single card instance.

    Attributes:
        id: Canonical card identifier.
        name: Printed card name.
        type: Printed card type line.
        desc: Printed rules text.
        atk: Printed attack value when present.
        def_: Printed defense value when present.
        level: Printed level when present.
        race: Printed monster race when present.
        attribute: Printed attribute when present.
    """

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


class Deck(BaseModel):
    """A draw-capable ordered deck for the current slice.

    Attributes:
        cards: Remaining cards in draw order.
    """

    model_config = ConfigDict(validate_assignment=True)

    cards: list[Card]

    def draw(self, num: int = 1) -> list[Card]:
        if num < 0:
            raise ValueError(f"draw count must be non-negative: {num}")
        if num > len(self.cards):
            raise ValueError(f"cannot draw {num} cards from deck of size {len(self.cards)}")

        drawn = self.cards[:num]
        del self.cards[:num]
        return drawn


class Player(BaseModel):
    """Runtime state owned by one duel participant.

    Attributes:
        label: Presentation label for the player.
        main_deck: Draw-capable main deck.
        extra_deck: Extra-deck contents kept separate from draw behavior.
        hand: Private cards currently in hand.
        monster_zones: This player's monster-zone occupancy.
    """

    model_config = ConfigDict(validate_assignment=True)

    label: str
    main_deck: Deck
    extra_deck: list[Card]
    hand: list[Card] = Field(default_factory=list)
    monster_zones: list[Card | None] = Field(default_factory=lambda: [None])


class DuelState(BaseModel):
    """Kernel-owned runtime state and observe composition boundary.

    Attributes:
        players: The two duel participants.
        current_player: The player whose turn it currently is.
        current_turn: One-based turn counter.
        phase: Current turn phase.
        normal_summon_used: Whether the current player has used a normal summon.
    """

    model_config = ConfigDict(validate_assignment=True)

    _VISIBLE_PLAYER_FIELDS: ClassVar[tuple[tuple[str, Callable[[Player], object]], ...]] = (
        ("label", lambda player: player.label),
        ("monster_zones", lambda player: tuple(player.monster_zones)),
    )
    _PUBLIC_VIEW_FIELDS: ClassVar[tuple[tuple[str, Callable[["DuelState"], object]], ...]] = (
        ("current_turn", lambda state: state.current_turn),
        ("phase", lambda state: state.phase),
        ("normal_summon_used", lambda state: state.normal_summon_used),
    )

    players: tuple[Player, Player]
    current_player: Player
    current_turn: int
    phase: Phase
    normal_summon_used: bool = False

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
    """Public duel facts visible regardless of player perspective.

    Attributes:
        current_turn: One-based turn counter.
        phase: Current turn phase.
        normal_summon_used: Whether the turn's normal summon has been used.
    """

    model_config = ConfigDict(frozen=True)

    current_turn: int
    phase: Phase
    normal_summon_used: bool


class VisiblePlayer(BaseModel):
    """Player-facing visible information for one side of the field.

    Attributes:
        label: Player label visible in the current view.
        monster_zones: Visible monster-zone occupancy for that side.
    """

    model_config = ConfigDict(frozen=True)

    label: str
    monster_zones: tuple[Card | None, ...]


class PlayerView(BaseModel):
    """Access-controlled player-facing view of the duel state.

    Attributes:
        viewer: The observing player's visible side.
        opponent: The opposing visible side.
        current_player: The side whose turn it currently is.
        public: Public duel facts shared across all perspectives.
    """

    model_config = ConfigDict(frozen=True)

    viewer: VisiblePlayer
    opponent: VisiblePlayer
    current_player: VisiblePlayer
    public: PublicView
