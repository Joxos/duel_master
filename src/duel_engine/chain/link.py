from __future__ import annotations

from dataclasses import dataclass

from duel_engine.timing import SpellSpeed


@dataclass(frozen=True, slots=True)
class ChainLink:
    chain_id: int
    effect_id: str
    source_card_id: str
    controller: str
    targets: tuple[str, ...]
    spell_speed: SpellSpeed
