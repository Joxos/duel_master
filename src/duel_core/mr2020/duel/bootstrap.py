from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from affairon.composer import PluginComposer

if TYPE_CHECKING:
    from duel_core.mr2020.duel.models import Duel

PYPROJECT_PATH = Path(__file__).resolve().parents[4] / "pyproject.toml"


def rebuild_model_graph() -> None:
    from duel_core.mr2020.battle.affairs import Attack, rebuild_battle_models
    from duel_core.mr2020.card.affairs import MoveCard, rebuild_card_affairs
    from duel_core.mr2020.card.models import Card, REPRESENTATION, RuntimeCard
    from duel_core.mr2020.draw.affairs import Draw, rebuild_draw_models
    from duel_core.mr2020.duel.affairs import (
        AvailableActions,
        CompletedAffair,
        DuelAffair,
        DuelAffairWithRequester,
        DuelInit,
        MultiAction,
        rebuild_duel_models,
    )
    from duel_core.mr2020.duel.models import Duel
    from duel_core.mr2020.forbid.affairs import Forbid
    from duel_core.mr2020.life_point.affairs import LpVary, rebuild_life_point_models
    from duel_core.mr2020.phase.affairs import EnterPhase, ExitPhase, rebuild_phase_models
    from duel_core.mr2020.phase.models import Phase
    from duel_core.mr2020.player.affairs import SetPlayers, rebuild_player_affairs
    from duel_core.mr2020.player.models import Player, Zone
    from duel_core.mr2020.summon.affairs import NormalSummon, rebuild_summon_models
    from duel_core.mr2020.timing.affairs import (
        AtomicAction,
        ExposedUserAction,
        TimingAction,
        rebuild_timing_models,
    )
    from duel_core.mr2020.turn.affairs import AdvanceTurn, rebuild_turn_models
    from duel_core.mr2020.view.models import (
        PlayerView,
        PublicPlayerView,
        PublicView,
        rebuild_view_models,
    )

    namespace = {
        "AdvanceTurn": AdvanceTurn,
        "AtomicAction": AtomicAction,
        "Attack": Attack,
        "AvailableActions": AvailableActions,
        "Card": Card,
        "CompletedAffair": CompletedAffair,
        "Draw": Draw,
        "Duel": Duel,
        "DuelAffair": DuelAffair,
        "DuelAffairWithRequester": DuelAffairWithRequester,
        "DuelInit": DuelInit,
        "EnterPhase": EnterPhase,
        "ExposedUserAction": ExposedUserAction,
        "ExitPhase": ExitPhase,
        "Forbid": Forbid,
        "LpVary": LpVary,
        "MoveCard": MoveCard,
        "MultiAction": MultiAction,
        "NormalSummon": NormalSummon,
        "Phase": Phase,
        "Player": Player,
        "SetPlayers": SetPlayers,
        "PlayerView": PlayerView,
        "PublicPlayerView": PublicPlayerView,
        "PublicView": PublicView,
        "REPRESENTATION": REPRESENTATION,
        "RuntimeCard": RuntimeCard,
        "TimingAction": TimingAction,
        "Zone": Zone,
    }
    Forbid.model_rebuild(_types_namespace=namespace)
    rebuild_duel_models(namespace)
    rebuild_timing_models(namespace)
    rebuild_phase_models(namespace)
    rebuild_turn_models(namespace)
    rebuild_player_affairs(namespace)
    rebuild_card_affairs(namespace)
    rebuild_draw_models(namespace)
    rebuild_summon_models(namespace)
    rebuild_battle_models(namespace)
    rebuild_life_point_models(namespace)
    rebuild_view_models(namespace)


def compose(duel: Duel) -> None:
    composer = PluginComposer(duel.dispatcher)
    composer.compose_from_pyproject(PYPROJECT_PATH, profile="duel")
