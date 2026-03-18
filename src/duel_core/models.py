from pydantic import BaseModel, ConfigDict, Field

from duel_core.phase import Phase


class Deck(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    cards: list[str]

    def draw(self, num: int = 1) -> list[str]:
        if num < 0:
            raise ValueError(f"draw count must be non-negative: {num}")
        if num > len(self.cards):
            raise ValueError(f"cannot draw {num} cards from deck of size {len(self.cards)}")

        drawn = self.cards[:num]
        del self.cards[:num]
        return drawn


class Player(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    main_deck: Deck
    extra_deck: Deck
    hand: list[str] = Field(default_factory=list)


class DuelState(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    players: tuple[Player, Player]
    current_player: Player
    current_turn: int
    phase: Phase


class DuelView(BaseModel):
    model_config = ConfigDict(frozen=True)

    viewer: Player
    current_player: Player
    current_turn: int
    phase: Phase
    hand_sizes: tuple[int, int]
    deck_sizes: tuple[int, int]
