"""Inward RNG port used by deterministic rules."""

from __future__ import annotations

from typing import Protocol, Self


class RandomSource(Protocol):
    """Immutable random source. Every draw returns next stream state."""

    @property
    def draws(self) -> int: ...

    def next_int(self, low: int, high: int) -> tuple[int, Self]: ...

    def die(self, sides: int) -> tuple[int, Self]: ...
