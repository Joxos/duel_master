from __future__ import annotations

from dataclasses import dataclass, field

from duel_engine.chain.link import ChainLink
from duel_engine.timing import SpellSpeed


@dataclass(slots=True)
class ChainBuilder:
    _links: list[ChainLink] = field(default_factory=list)
    _closed: bool = False

    def add_link(
        self,
        *,
        effect_id: str,
        source_card_id: str,
        targets: list[str] | tuple[str, ...],
        controller: str,
        spell_speed: SpellSpeed,
    ) -> ChainLink:
        if self._closed:
            raise ValueError("Chain is closed and cannot accept new links")

        chain_link = ChainLink(
            chain_id=len(self._links) + 1,
            effect_id=effect_id,
            source_card_id=source_card_id,
            controller=controller,
            targets=tuple(targets),
            spell_speed=spell_speed,
        )
        self._links.append(chain_link)
        return chain_link

    def build_chain(self) -> list[ChainLink]:
        return list(reversed(self._links))

    def close_chain(self) -> None:
        self._closed = True
