from __future__ import annotations

from .card import Card
from .player import Player
from .state import GameState, SCHEMA_VERSION


def _project_card(card: Card, reveal: bool) -> dict[str, object]:
    projected_name = card.name if reveal else None
    projected_type = card.card_type if reveal else None
    return {
        "id": card.visible_identifier(reveal=reveal),
        "face_up": card.face_up,
        "owner_id": card.owner_id,
        "name": projected_name,
        "card_type": projected_type,
    }


def _project_player(player: Player, viewer_id: str) -> dict[str, object]:
    is_self = player.id == viewer_id

    return {
        "id": player.id,
        "life_points": player.life_points,
        "hand": [
            _project_card(card, reveal=is_self or card.face_up) for card in player.hand
        ],
        "deck": [_project_card(card, reveal=False) for card in player.deck],
        "graveyard": [_project_card(card, reveal=True) for card in player.graveyard],
        "banished": [
            _project_card(card, reveal=card.face_up) for card in player.banished
        ],
        "extra_deck": [
            _project_card(card, reveal=is_self or card.face_up)
            for card in player.extra_deck
        ],
    }


def player_view(state: GameState, player_id: str) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "turn": state.turn,
        "phase": state.phase,
        "step": state.step,
        "priority_player": state.priority_player,
        "players": [
            _project_player(player, viewer_id=player_id) for player in state.players
        ],
    }


def omniscient_view(state: GameState) -> dict[str, object]:
    return state.to_dict()
