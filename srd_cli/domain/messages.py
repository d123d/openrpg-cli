"""Closed, versioned command and event messages."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, ClassVar, Mapping, TypeAlias

from .state import SCHEMA_VERSION, freeze


@dataclass(frozen=True, slots=True)
class Message:
    id: str
    aggregate_id: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    schema_version: int = SCHEMA_VERSION
    type_tag: ClassVar[str]

    def __post_init__(self) -> None:
        if not self.id or not self.aggregate_id:
            raise ValueError("message id and aggregate id are required")
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("unsupported message schema version")
        object.__setattr__(self, "payload", freeze(self.payload))


@dataclass(frozen=True, slots=True)
class CreateGame(Message):
    type_tag: ClassVar[str] = "create_game"


@dataclass(frozen=True, slots=True)
class PutEntity(Message):
    type_tag: ClassVar[str] = "put_entity"


@dataclass(frozen=True, slots=True)
class RollDie(Message):
    type_tag: ClassVar[str] = "roll_die"


@dataclass(frozen=True, slots=True)
class RecordLegacy(Message):
    type_tag: ClassVar[str] = "record_legacy"


@dataclass(frozen=True, slots=True)
class GameCreated(Message):
    type_tag: ClassVar[str] = "game_created"


@dataclass(frozen=True, slots=True)
class EntityPut(Message):
    type_tag: ClassVar[str] = "entity_put"


@dataclass(frozen=True, slots=True)
class DieRolled(Message):
    type_tag: ClassVar[str] = "die_rolled"


@dataclass(frozen=True, slots=True)
class LegacyRecorded(Message):
    type_tag: ClassVar[str] = "legacy_recorded"


@dataclass(frozen=True, slots=True)
class CommandRejected(Message):
    type_tag: ClassVar[str] = "command_rejected"


Command: TypeAlias = CreateGame | PutEntity | RollDie | RecordLegacy
Event: TypeAlias = GameCreated | EntityPut | DieRolled | LegacyRecorded | CommandRejected
COMMAND_TYPES = MappingProxyType({x.type_tag: x for x in (CreateGame, PutEntity, RollDie, RecordLegacy)})
EVENT_TYPES = MappingProxyType(
    {x.type_tag: x for x in (GameCreated, EntityPut, DieRolled, LegacyRecorded, CommandRejected)}
)


def command_from_tag(tag: str, **kwargs: Any) -> Command:
    try:
        return COMMAND_TYPES[tag](**kwargs)
    except KeyError as exc:
        raise ValueError(f"unknown command tag: {tag}") from exc


def event_from_tag(tag: str, **kwargs: Any) -> Event:
    try:
        return EVENT_TYPES[tag](**kwargs)
    except KeyError as exc:
        raise ValueError(f"unknown event tag: {tag}") from exc
