"""SEGOC (Simultaneous Effects Go On Chain) sorting utilities.

Provides static helpers to order effect resolution lists according to
commonly-used rules: mandatory effects before optional, and turn-player
effects before opposing player's effects.

The helpers are permissive about effect representation: an effect may be
any object with attributes or a dict. Common field names are checked.
"""

from typing import Any, Iterable, List


class SEGOC:
    @staticmethod
    def _is_mandatory(effect: Any) -> bool:
        """Return True if effect is mandatory.

        Checks common keys/attributes: 'is_mandatory', 'mandatory', 'required'.
        Non-boolean truthy values are treated as True. Missing -> False.
        """
        if effect is None:
            return False
        # dict-like
        if isinstance(effect, dict):
            for key in ("is_mandatory", "mandatory", "required"):
                if key in effect:
                    return bool(effect[key])
            return False

        # object-like: check attributes
        for attr in ("is_mandatory", "mandatory", "required"):
            val = getattr(effect, attr, None)
            if val is not None:
                return bool(val)
        return False

    @staticmethod
    def _owner_id(effect: Any) -> Any:
        """Extract a player/owner id from an effect.

        Checks common keys/attributes and returns the first non-None value.
        If nothing found returns None.
        """
        if effect is None:
            return None
        if isinstance(effect, dict):
            for key in (
                "turn_player",
                "player_id",
                "controller_id",
                "owner",
                "owner_id",
                "player",
            ):
                if key in effect:
                    return effect[key]
            return None

        for attr in (
            "turn_player",
            "player_id",
            "controller_id",
            "owner",
            "owner_id",
            "player",
        ):
            val = getattr(effect, attr, None)
            if val is not None:
                return val
        return None

    @staticmethod
    def mandatory_first(effects: Iterable[Any]) -> List[Any]:
        """Return a new list with mandatory effects before optional.

        The relative order among mandatory effects is preserved, likewise for
        optional effects (stable sort semantics).
        """
        if effects is None:
            return []
        # stable sort by key: mandatory -> 0, optional -> 1
        return sorted(list(effects), key=lambda e: 0 if SEGOC._is_mandatory(e) else 1)

    @staticmethod
    def then_by_turn_player(effects: Iterable[Any], turn_player_id: Any) -> List[Any]:
        """Return a new list with effects belonging to turn_player_id first.

        Relative order is preserved (stable). Owner/player extraction uses a
        best-effort approach checking common attribute and dict keys.
        """
        if effects is None:
            return []
        return sorted(
            list(effects),
            key=lambda e: 0 if SEGOC._owner_id(e) == turn_player_id else 1,
        )
