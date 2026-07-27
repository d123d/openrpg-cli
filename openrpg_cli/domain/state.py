"""Immutable, schema-versioned authoritative state."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .provenance import RuntimeContentRef

SCHEMA_VERSION = 1


def freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(k): freeze(v) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(freeze(v) for v in value)
    if isinstance(value, set):
        return frozenset(freeze(v) for v in value)
    return value


@dataclass(frozen=True, slots=True)
class EntityState:
    id: str
    data: Mapping[str, Any] = field(default_factory=dict)
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("entity id is required")
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("unsupported state schema version")
        object.__setattr__(self, "data", freeze(self.data))


@dataclass(frozen=True, slots=True)
class ActorState(EntityState):
    team_id: str | None = None


@dataclass(frozen=True, slots=True)
class TeamState(EntityState):
    actor_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class SceneState(EntityState):
    runtime_content: RuntimeContentRef | None = None


@dataclass(frozen=True, slots=True)
class EncounterState(EntityState):
    actor_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ClockState(EntityState):
    value: int = 0
    maximum: int = 1


@dataclass(frozen=True, slots=True)
class ResourceState(EntityState):
    current: int = 0
    maximum: int = 0


@dataclass(frozen=True, slots=True)
class EffectState(EntityState):
    source_id: str | None = None


@dataclass(frozen=True, slots=True)
class GameState:
    id: str
    schema_version: int = SCHEMA_VERSION
    actors: tuple[ActorState, ...] = ()
    teams: tuple[TeamState, ...] = ()
    scenes: tuple[SceneState, ...] = ()
    encounters: tuple[EncounterState, ...] = ()
    clocks: tuple[ClockState, ...] = ()
    resources: tuple[ResourceState, ...] = ()
    effects: tuple[EffectState, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("game id is required")
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("unsupported state schema version")
        object.__setattr__(self, "metadata", freeze(self.metadata))
        for name in ("actors", "teams", "scenes", "encounters", "clocks", "resources", "effects"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
