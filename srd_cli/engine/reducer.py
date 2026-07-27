"""Pure allowlisted command reducer."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable

from srd_cli.domain.messages import (
    Command,
    CommandRejected,
    CreateGame,
    DieRolled,
    EntityPut,
    Event,
    GameCreated,
    LegacyRecorded,
    PutEntity,
    RecordLegacy,
    RollDie,
)
from srd_cli.domain.state import (
    ActorState,
    ClockState,
    EffectState,
    EncounterState,
    GameState,
    ResourceState,
    SceneState,
    TeamState,
)

from .rng import GameRNG


@dataclass(frozen=True, slots=True)
class ReductionResult:
    state: GameState
    events: tuple[Event, ...]
    rng: GameRNG


def _event(cls: type[Event], command: Command, payload: dict) -> Event:
    return cls(id=f"{command.id}:event", aggregate_id=command.aggregate_id, payload=payload)


def _create(state: GameState, cmd: CreateGame, rng: GameRNG) -> ReductionResult:
    if state.id != cmd.aggregate_id:
        raise ValueError("aggregate id mismatch")
    return ReductionResult(state, (_event(GameCreated, cmd, {"game_id": state.id}),), rng)


def _put(state: GameState, cmd: PutEntity, rng: GameRNG) -> ReductionResult:
    kind, entity_id = str(cmd.payload.get("kind", "")), str(cmd.payload.get("id", ""))
    data = cmd.payload.get("data", {})
    table = {
        "actor": ("actors", ActorState),
        "team": ("teams", TeamState),
        "scene": ("scenes", SceneState),
        "encounter": ("encounters", EncounterState),
        "clock": ("clocks", ClockState),
        "resource": ("resources", ResourceState),
        "effect": ("effects", EffectState),
    }
    if kind not in table or not entity_id:
        raise ValueError("invalid entity kind or id")
    field, cls = table[kind]
    entity = cls(id=entity_id, data=data)
    current = getattr(state, field)
    updated = tuple(entity if x.id == entity_id else x for x in current)
    if not any(x.id == entity_id for x in current):
        updated += (entity,)
    return ReductionResult(
        replace(state, **{field: updated}),
        (_event(EntityPut, cmd, {"kind": kind, "id": entity_id}),),
        rng,
    )


def _roll(state: GameState, cmd: RollDie, rng: GameRNG) -> ReductionResult:
    sides = int(cmd.payload.get("sides", 0))
    value, next_rng = rng.die(sides)
    return ReductionResult(state, (_event(DieRolled, cmd, {"sides": sides, "result": value}),), next_rng)


def _legacy(state: GameState, cmd: RecordLegacy, rng: GameRNG) -> ReductionResult:
    return ReductionResult(state, (_event(LegacyRecorded, cmd, dict(cmd.payload)),), rng)


Handler = Callable[[GameState, Command, GameRNG], ReductionResult]
HANDLERS: dict[type, Handler] = {CreateGame: _create, PutEntity: _put, RollDie: _roll, RecordLegacy: _legacy}


def reduce_command(state: GameState, command: Command, rng: GameRNG) -> ReductionResult:
    handler = HANDLERS.get(type(command))
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
