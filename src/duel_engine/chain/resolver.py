from __future__ import annotations

from dataclasses import dataclass, field

from duel_engine.chain.link import ChainLink


@dataclass(slots=True)
class ChainResolver:
    _negated_chain_ids: set[int] = field(default_factory=set)

    def negate(self, chain_link: ChainLink) -> None:
        self._negated_chain_ids.add(chain_link.chain_id)

    def resolve(
        self, chain: list[ChainLink] | tuple[ChainLink, ...]
    ) -> list[dict[str, object]]:
        return self.apply_effects(chain)

    def apply_effects(
        self, chain: list[ChainLink] | tuple[ChainLink, ...]
    ) -> list[dict[str, object]]:
        results: list[dict[str, object]] = []
        for link in chain:
            is_negated = link.chain_id in self._negated_chain_ids
            results.append(
                {
                    "chain_id": link.chain_id,
                    "effect_id": link.effect_id,
                    "controller": link.controller,
                    "source_card_id": link.source_card_id,
                    "targets": list(link.targets),
                    "status": "negated" if is_negated else "applied",
                }
            )
        return results
