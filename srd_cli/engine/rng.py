"""Small explicit immutable PCG-style RNG."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GameRNG:
    state: int
    draws: int = 0

    def next_int(self, low: int, high: int) -> tuple[int, "GameRNG"]:
        if low > high:
            raise ValueError("low must not exceed high")
        state = (self.state * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
        value = low + state % (high - low + 1)
        return value, GameRNG(state, self.draws + 1)

    def die(self, sides: int) -> tuple[int, "GameRNG"]:
        if sides < 2:
            raise ValueError("die must have at least 2 sides")
        return self.next_int(1, sides)
