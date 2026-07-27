"""Explicit command-to-handler composition."""

from __future__ import annotations

from collections.abc import Callable, Mapping

from openrpg_cli.domain.messages import Command, CommandRejected
from openrpg_cli.domain.state import GameState
from openrpg_cli.engine.rng import DeterministicRNG
from openrpg_cli.engine.types import ReductionResult

Handler = Callable[[GameState, Command, DeterministicRNG], ReductionResult]


class CommandRouter:
    """Routes exact command types through an immutable handler registry."""

    def __init__(self, handlers: Mapping[type[Command], Handler]) -> None:
        self._handlers = dict(handlers)

    @property
    def handlers(self) -> Mapping[type[Command], Handler]:
        return self._handlers

    def reduce(
        self, state: GameState, command: Command, rng: DeterministicRNG
    ) -> ReductionResult:
        handler = self._handlers.get(type(command))
        try:
            if handler is None:
                raise ValueError("unknown command type")
            return handler(state, command, rng)
        except (ValueError, TypeError, KeyError) as exc:
            event = CommandRejected(
                id=f"{command.id}:rejected",
                aggregate_id=command.aggregate_id,
                payload={"command_type": command.type_tag, "reason": str(exc)},
            )
            return ReductionResult(state, (event,), rng)
