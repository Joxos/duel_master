from __future__ import annotations

from typing import Self, cast

from duel_core.models import FrozenModel
from duel_core.mr2020.models.card import RuntimeCard
from duel_core.mr2020.models.player import Player
from duel_core.mr2020.models.state import DuelState
from duel_core.phase import Phase


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


PublicPlayerView.model_rebuild(_types_namespace={"RuntimeCard": RuntimeCard, "Player": Player})
PublicView.model_rebuild(
    _types_namespace={
        "DuelState": DuelState,
        "PublicPlayerView": PublicPlayerView,
    }
)
PlayerView.model_rebuild(
    _types_namespace={
        "RuntimeCard": RuntimeCard,
        "Player": Player,
        "DuelState": DuelState,
        "PublicView": PublicView,
    }
)
