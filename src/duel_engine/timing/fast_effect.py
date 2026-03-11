from __future__ import annotations

from dataclasses import dataclass

from .windows import SpellSpeed, TimingWindow

_OPEN_WINDOWS: frozenset[TimingWindow] = frozenset(
    {
        TimingWindow.OPEN,
        TimingWindow.DRAW,
        TimingWindow.STANDBY,
        TimingWindow.MAIN1_OPEN,
        TimingWindow.BATTLE_START,
        TimingWindow.BATTLE_END,
        TimingWindow.MAIN2_OPEN,
        TimingWindow.END_OPEN,
    }
)


@dataclass(frozen=True, slots=True)
class FastEffect:
    effect_id: str
    controller: str
    spell_speed: SpellSpeed


@dataclass(frozen=True, slots=True)
class FastEffectResolver:
    def allowed_spell_speeds(
        self,
        window: TimingWindow,
        is_chain_response: bool,
    ) -> tuple[SpellSpeed, ...]:
        if is_chain_response:
            return (SpellSpeed.SS2, SpellSpeed.SS3)
        if window in _OPEN_WINDOWS:
            return (SpellSpeed.SS1, SpellSpeed.SS2, SpellSpeed.SS3)
        if window == TimingWindow.DAMAGE:
            return (SpellSpeed.SS2, SpellSpeed.SS3)
        return ()

    def activatable_effects(
        self,
        *,
        effects: tuple[FastEffect, ...],
        window: TimingWindow,
        priority_player: str,
        is_chain_response: bool,
    ) -> list[FastEffect]:
        allowed_speeds = set(
            self.allowed_spell_speeds(
                window=window,
                is_chain_response=is_chain_response,
            )
        )

        return [
            effect
            for effect in effects
            if effect.controller == priority_player
            and effect.spell_speed in allowed_speeds
        ]

    def build_chain_candidates(
        self,
        *,
        effects: tuple[FastEffect, ...],
        window: TimingWindow,
        priority_player: str,
        is_chain_response: bool,
    ) -> dict[str, list[FastEffect]]:
        candidates = self.activatable_effects(
            effects=effects,
            window=window,
            priority_player=priority_player,
            is_chain_response=is_chain_response,
        )
        grouped: dict[str, list[FastEffect]] = {
            SpellSpeed.SS1.name: [],
            SpellSpeed.SS2.name: [],
            SpellSpeed.SS3.name: [],
        }
        for effect in candidates:
            grouped[effect.spell_speed.name].append(effect)
        return grouped
