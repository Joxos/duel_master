from __future__ import annotations

from typing import MutableSequence, Sequence, TypeVar

T = TypeVar("T")


class RNG:
    _MASK_64 = (1 << 64) - 1
    _MASK_32 = (1 << 32) - 1
    _MULTIPLIER = 6364136223846793005
    _INCREMENT = 1442695040888963407

    def __init__(self, seed: int):
        self._state = 0
        self._seed(seed)

    def _seed(self, seed: int) -> None:
        mixed_seed = seed & self._MASK_64
        self._state = (mixed_seed + self._INCREMENT) & self._MASK_64
        self._next_uint32()

    def _next_uint32(self) -> int:
        oldstate = self._state
        self._state = (oldstate * self._MULTIPLIER + self._INCREMENT) & self._MASK_64
        xorshifted = (((oldstate >> 18) ^ oldstate) >> 27) & self._MASK_32
        rot = (oldstate >> 59) & 31
        return ((xorshifted >> rot) | (xorshifted << ((-rot) & 31))) & self._MASK_32

    def randint(self, a: int, b: int) -> int:
        if a > b:
            raise ValueError("a must be <= b")
        span = b - a + 1
        threshold = (-span) % span
        while True:
            r = self._next_uint32()
            if r >= threshold:
                return a + (r % span)

    def shuffle(self, seq: MutableSequence[T]) -> MutableSequence[T]:
        for i in range(len(seq) - 1, 0, -1):
            j = self.randint(0, i)
            seq[i], seq[j] = seq[j], seq[i]
        return seq

    def choice(self, seq: Sequence[T]) -> T:
        if not seq:
            raise IndexError("cannot choose from an empty sequence")
        return seq[self.randint(0, len(seq) - 1)]
