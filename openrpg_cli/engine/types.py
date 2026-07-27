"""Engine result values shared by router and handlers."""

from __future__ import annotations

from dataclasses import dataclass

from openrpg_cli.domain.messages import Event
from openrpg_cli.domain.state import GameState
from openrpg_cli.engine.rng import DeterministicRNG


@dataclass(frozen=True, slots=True)
class ReductionResult:
    state: GameState
    events: tuple[Event, ...]
    rng: DeterministicRNG
