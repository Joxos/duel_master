from __future__ import annotations

from dataclasses import replace

from duel_engine import __version__
from duel_engine.actions import Action, ActionType, InvalidActionError, legal_actions
from duel_engine.models import Card, GameState, Player
from duel_engine.replay import Replay, ReplayData
from duel_engine.rng import RNG, final_state_hash

_PHASE_ORDER = ("DRAW", "STANDBY", "MAIN1", "BATTLE", "MAIN2", "END")


def _turn_player_id(state: GameState) -> str:
    """Get the current turn player's id.

    Args:
        state: Current duel state.

    Returns:
        Player id that owns the current turn.
    """
    return state.players[(state.turn - 1) % 2].id


def _next_phase(current_phase: str) -> str:
    """Get the next phase in the simplified phase order.

    Args:
        current_phase: Current phase label.

    Returns:
        Next phase label.
    """
    idx = _PHASE_ORDER.index(current_phase)
    return _PHASE_ORDER[(idx + 1) % len(_PHASE_ORDER)]


def _default_deck(owner_id: str, deck_size: int) -> list[Card]:
    """Create a placeholder deck for one player.

    Args:
        owner_id: Player id owning the deck.
        deck_size: Number of cards in the deck.

    Returns:
        A list of placeholder monster cards.
    """
    return [
        Card(name=f"{owner_id}_card_{i}", card_type="MONSTER", owner_id=owner_id, face_up=False)
        for i in range(deck_size)
    ]


class Duel:
    """Stateful single-duel facade for library users.

    Args:
        state: Initial duel state.
        seed: Deterministic RNG seed for replay metadata.
        ruleset_id: Ruleset identifier for replay metadata.
        policy: Default action-selection policy.
    """

    def __init__(
        self,
        *,
        state: GameState,
        seed: int,
        ruleset_id: str = "MR2020",
        policy: str = "deterministic-default",
    ) -> None:
        self.state = state
        self.seed = seed
        self.ruleset_id = ruleset_id
        self.policy = policy
        self._initial_state_hash = final_state_hash(state.to_dict())
        self._actions_log: list[dict[str, object]] = []
        self._choices_log: list[dict[str, object]] = []
        self._events: list[dict[str, object]] = [
            {
                "type": "initial_state",
                "state": state.to_dict(),
                "state_hash": self._initial_state_hash,
            }
        ]

    @classmethod
    def create(
        cls,
        *,
        seed: int,
        deck_size: int = 40,
        hand_size: int = 5,
        p1_deck: list[Card] | None = None,
        p2_deck: list[Card] | None = None,
        policy: str = "deterministic-default",
    ) -> "Duel":
        """Create a duel from shuffled decks.

        Args:
            seed: Deterministic RNG seed.
            deck_size: Deck size used when decks are not provided.
            hand_size: Opening hand size.
            p1_deck: Optional explicit deck list for player 1.
            p2_deck: Optional explicit deck list for player 2.
            policy: Default action-selection policy.

        Returns:
            New duel instance with initialized state.
        """
        state = init_duel(
            seed=seed,
            deck_size=deck_size,
            hand_size=hand_size,
            p1_deck=p1_deck,
            p2_deck=p2_deck,
        )
        return cls(state=state, seed=seed, policy=policy)

    def turn_player_id(self) -> str:
        """Get the active turn player's id.

        Returns:
            Current turn player id.
        """
        return _turn_player_id(self.state)

    def legal_actions(self, player_id: str | None = None) -> list[Action]:
        """List legal actions for a player.

        Args:
            player_id: Target player id; defaults to current turn player.

        Returns:
            Legal actions available in current state.
        """
        target_player = player_id or self.turn_player_id()
        return legal_actions(self.state, target_player)

    def select_action(self, policy: str | None = None) -> Action:
        """Select one action according to policy.

        Args:
            policy: Policy override; defaults to duel policy.

        Returns:
            Selected action.

        Raises:
            ValueError: If no action exists or policy is unsupported.
        """
        active_policy = policy or self.policy
        actions = self.legal_actions(self.turn_player_id())
        if not actions:
            raise ValueError("No legal actions available")
        if active_policy == "deterministic-default":
            return next(
                (a for a in actions if a.action_type == ActionType.PASS_PRIORITY), actions[0]
            )
        raise ValueError(f"Unsupported policy: {active_policy}")

    def apply_action(self, action: Action) -> GameState:
        """Apply one action and record replay event data.

        Args:
            action: Action to apply.

        Returns:
            Updated duel state.
        """
        step_index = len(self._actions_log)
        self._actions_log.append({"step": step_index, **action.to_dict()})
        self._choices_log.append(
            {
                "step": step_index,
                "policy": self.policy,
                "request": "select_action",
                "choice": action.action_type.value,
            }
        )
        self.state = step(self.state, action)
        self._events.append(
            {
                "type": "state_after_action",
                "step": step_index,
                "state_hash": final_state_hash(self.state.to_dict()),
                "turn": self.state.turn,
                "phase": self.state.phase,
            }
        )
        return self.state

    def run(self, *, steps: int = 50, policy: str | None = None) -> GameState:
        """Run duel loop for up to N steps.

        Args:
            steps: Maximum number of action iterations.
            policy: Optional policy override.

        Returns:
            Final duel state after execution.
        """
        if policy is not None:
            self.policy = policy
        for _ in range(steps):
            actions = self.legal_actions(self.turn_player_id())
            if not actions:
                break
            action = self.select_action(self.policy)
            self.apply_action(action)
        return self.state

    def to_replay(self) -> Replay:
        """Build replay object from recorded duel actions.

        Returns:
            Replay object containing action, choice, and event history.
        """
        final_hash = final_state_hash(self.state.to_dict())
        events = list(self._events)
        events.append({"type": "final_state_hash", "state_hash": final_hash})
        return Replay(
            data=ReplayData(
                engine_version=__version__,
                ruleset_id=self.ruleset_id,
                seed=self.seed,
                initial_state_hash=self._initial_state_hash,
                actions=list(self._actions_log),
                choices=list(self._choices_log),
                events=events,
            )
        )


def init_duel(
    *,
    seed: int,
    deck_size: int = 40,
    hand_size: int = 5,
    p1_deck: list[Card] | None = None,
    p2_deck: list[Card] | None = None,
) -> GameState:
    """Initialize a single-duel state with shuffled decks and opening hands.

    Args:
        seed: Deterministic RNG seed.
        deck_size: Deck size used when decks are not provided.
        hand_size: Opening hand size.
        p1_deck: Optional explicit deck list for player 1.
        p2_deck: Optional explicit deck list for player 2.

    Returns:
        Initialized duel state in DRAW phase for turn player p1.
    """
    p1_id = "p1"
    p2_id = "p2"

    p1_cards = (
        p1_deck if p1_deck is not None else _default_deck(owner_id=p1_id, deck_size=deck_size)
    )
    p2_cards = (
        p2_deck if p2_deck is not None else _default_deck(owner_id=p2_id, deck_size=deck_size)
    )

    rng = RNG(seed)
    p1_draw_pile = list(p1_cards)
    p2_draw_pile = list(p2_cards)
    rng.shuffle(p1_draw_pile)
    rng.shuffle(p2_draw_pile)

    return GameState(
        players=(
            Player(
                id=p1_id, hand=tuple(p1_draw_pile[:hand_size]), deck=tuple(p1_draw_pile[hand_size:])
            ),
            Player(
                id=p2_id, hand=tuple(p2_draw_pile[:hand_size]), deck=tuple(p2_draw_pile[hand_size:])
            ),
        ),
        turn=1,
        phase="DRAW",
        step="OPEN",
        priority_player=p1_id,
    )


def step(state: GameState, action: Action) -> GameState:
    """Apply one action to the duel state.

    Args:
        state: Current duel state.
        action: Action to apply.

    Returns:
        Next duel state after applying the action.

    Raises:
        InvalidActionError: If the action is not legal in the current state.
    """
    available = {candidate.action_type for candidate in legal_actions(state, action.player_id)}
    if action.action_type not in available:
        raise InvalidActionError(f"Illegal action for current state: {action.action_type.value}")

    if action.action_type in (
        ActionType.PASS_PRIORITY,
        ActionType.DRAW_PHASE,
        ActionType.STANDBY_PHASE,
        ActionType.END_PHASE,
    ):
        next_phase = _next_phase(state.phase)
        if state.phase == "END" and next_phase == "DRAW":
            next_turn = state.turn + 1
            next_priority = state.players[(next_turn - 1) % 2].id
            return replace(
                state,
                turn=next_turn,
                phase="DRAW",
                step="OPEN",
                priority_player=next_priority,
            )
        return replace(
            state,
            phase=next_phase,
            step="OPEN",
            priority_player=_turn_player_id(state),
        )

    return state


def run_duel(
    *, seed: int, steps: int = 50, policy: str = "deterministic-default"
) -> tuple[GameState, Replay]:
    """Run a deterministic duel loop for a bounded number of steps.

    Args:
        seed: Deterministic RNG seed.
        steps: Maximum number of loop iterations.
        policy: Action selection policy name.

    Returns:
        Final state and generated replay object.

    Raises:
        ValueError: If an unsupported policy is requested.
    """
    duel = Duel.create(seed=seed, policy=policy)
    final_state = duel.run(steps=steps)
    return final_state, duel.to_replay()
