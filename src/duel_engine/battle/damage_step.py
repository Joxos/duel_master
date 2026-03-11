from __future__ import annotations

from enum import Enum


class DamageStep(str, Enum):
    START = "START"
    CALC = "CALC"
    RESPONSE = "RESPONSE"
    END = "END"


class DamageStepMachine:
    _ORDER: tuple[DamageStep, ...] = (
        DamageStep.START,
        DamageStep.CALC,
        DamageStep.RESPONSE,
        DamageStep.END,
    )

    _ALLOWED_EFFECTS: dict[DamageStep, frozenset[str]] = {
        DamageStep.START: frozenset({"mandatory_trigger", "damage_step_trigger"}),
        DamageStep.CALC: frozenset(
            {
                "mandatory_trigger",
                "damage_step_trigger",
                "atk_def_modifier",
            }
        ),
        DamageStep.RESPONSE: frozenset(
            {
                "mandatory_trigger",
                "damage_step_trigger",
                "quick",
                "counter",
            }
        ),
        DamageStep.END: frozenset({"mandatory_trigger", "damage_step_trigger"}),
    }

    def __init__(self, current_step: DamageStep = DamageStep.START) -> None:
        self.current_step = current_step

    def advance_step(self, step: DamageStep | None = None) -> DamageStep:
        target_step = step or self.current_step
        try:
            index = self._ORDER.index(target_step)
        except ValueError as exc:
            raise ValueError(f"Unsupported damage step: {target_step}") from exc

        if index == len(self._ORDER) - 1:
            raise ValueError("Cannot advance beyond END damage step")

        self.current_step = self._ORDER[index + 1]
        return self.current_step

    def can_activate(
        self, effect_type: str, current_step: DamageStep | None = None
    ) -> bool:
        step = current_step or self.current_step
        allowed = self._ALLOWED_EFFECTS.get(step)
        if allowed is None:
            return False
        return effect_type in allowed
