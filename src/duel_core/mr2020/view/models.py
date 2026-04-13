from __future__ import annotations

from typing import TYPE_CHECKING, Self, cast

from duel_core.models import FrozenModel
from duel_core.mr2020.card.models import RuntimeCard
from duel_core.mr2020.phase.models import Phase
from duel_core.mr2020.player.models import Player

if TYPE_CHECKING:
    from duel_core.mr2020.duel.models import Duel


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
    def from_duel(cls, duel: Duel) -> Self:
        public_players = tuple(
            PublicPlayerView.from_player(player) for player in duel.get_players()
        )
        return cls(
            current_player_label=duel.get_current_player().label,
            current_turn=duel.get_current_turn_count(),
            phase=duel.get_phase(),
            normal_summon_used=duel.get_normal_summon_used(),
            players=cast(tuple[PublicPlayerView, PublicPlayerView], public_players),
        )


class PlayerView(FrozenModel):
    player_label: str
    hand: tuple[RuntimeCard, ...]
    main_deck_size: int
    extra_deck_size: int
    public: PublicView

    @classmethod
    def from_duel(cls, duel: Duel, viewer: Player) -> Self:
        return cls(
            player_label=viewer.label,
            hand=tuple(viewer.hand),
            main_deck_size=len(viewer.main_deck.cards),
            extra_deck_size=len(viewer.extra_deck.cards),
            public=PublicView.from_duel(duel),
        )


def rebuild_view_models(namespace: dict[str, object]) -> None:
    for model in (PublicPlayerView, PublicView, PlayerView):
        model.model_rebuild(_types_namespace=namespace)
