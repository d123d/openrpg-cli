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
class ResolveTest(Message):
    type_tag: ClassVar[str] = "resolve_test"


@dataclass(frozen=True, slots=True)
class ApplyDamage(Message):
    type_tag: ClassVar[str] = "apply_damage"


@dataclass(frozen=True, slots=True)
class Heal(Message):
    type_tag: ClassVar[str] = "heal"


@dataclass(frozen=True, slots=True)
class ApplyEffect(Message):
    type_tag: ClassVar[str] = "apply_effect"


@dataclass(frozen=True, slots=True)
class RemoveEffect(Message):
    type_tag: ClassVar[str] = "remove_effect"


@dataclass(frozen=True, slots=True)
class AdvanceEffects(Message):
    type_tag: ClassVar[str] = "advance_effects"


@dataclass(frozen=True, slots=True)
class MakeDeathSave(Message):
    type_tag: ClassVar[str] = "make_death_save"


@dataclass(frozen=True, slots=True)
class Stabilize(Message):
    type_tag: ClassVar[str] = "stabilize"


@dataclass(frozen=True, slots=True)
class Recover(Message):
    type_tag: ClassVar[str] = "recover"

@dataclass(frozen=True, slots=True)
class StartEncounter(Message): type_tag: ClassVar[str] = "start_encounter"
@dataclass(frozen=True, slots=True)
class QueryLegalCommands(Message): type_tag: ClassVar[str] = "query_legal_commands"
@dataclass(frozen=True, slots=True)
class Act(Message): type_tag: ClassVar[str] = "act"
@dataclass(frozen=True, slots=True)
class Move(Message): type_tag: ClassVar[str] = "move"
@dataclass(frozen=True, slots=True)
class React(Message): type_tag: ClassVar[str] = "react"
@dataclass(frozen=True, slots=True)
class EndTurn(Message): type_tag: ClassVar[str] = "end_turn"


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


@dataclass(frozen=True, slots=True)
class ResolutionCompleted(Message):
    type_tag: ClassVar[str] = "resolution_completed"


@dataclass(frozen=True, slots=True)
class VitalityChanged(Message):
    type_tag: ClassVar[str] = "vitality_changed"


@dataclass(frozen=True, slots=True)
class EffectsChanged(Message):
    type_tag: ClassVar[str] = "effects_changed"
@dataclass(frozen=True, slots=True)
class TurnChanged(Message): type_tag: ClassVar[str] = "turn_changed"
@dataclass(frozen=True, slots=True)
class LegalCommandsListed(Message): type_tag: ClassVar[str] = "legal_commands_listed"
@dataclass(frozen=True, slots=True)
class ActionResolved(Message): type_tag: ClassVar[str] = "action_resolved"
@dataclass(frozen=True, slots=True)
class MovementResolved(Message): type_tag: ClassVar[str] = "movement_resolved"
@dataclass(frozen=True, slots=True)
class ReactionResolved(Message): type_tag: ClassVar[str] = "reaction_resolved"


Command: TypeAlias = (
    CreateGame
    | PutEntity
    | RollDie
    | RecordLegacy
    | ResolveTest
    | ApplyDamage
    | Heal
    | ApplyEffect
    | RemoveEffect
    | AdvanceEffects
    | MakeDeathSave
    | Stabilize
    | Recover
    | StartEncounter | QueryLegalCommands | Act | Move | React | EndTurn
)
Event: TypeAlias = (
    GameCreated
    | EntityPut
    | DieRolled
    | LegacyRecorded
    | ResolutionCompleted
    | VitalityChanged
    | EffectsChanged
    | CommandRejected
    | TurnChanged | LegalCommandsListed | ActionResolved | MovementResolved | ReactionResolved
)
COMMAND_TYPES = MappingProxyType(
    {
        x.type_tag: x
        for x in (
            CreateGame,
            PutEntity,
            RollDie,
            RecordLegacy,
            ResolveTest,
            ApplyDamage,
            Heal,
            ApplyEffect,
            RemoveEffect,
            AdvanceEffects,
            MakeDeathSave,
            Stabilize,
            Recover,
            StartEncounter, QueryLegalCommands, Act, Move, React, EndTurn,
        )
    }
)
EVENT_TYPES = MappingProxyType(
    {
        x.type_tag: x
        for x in (
            GameCreated,
            EntityPut,
            DieRolled,
            LegacyRecorded,
            ResolutionCompleted,
            VitalityChanged,
            EffectsChanged,
            CommandRejected,
            TurnChanged, LegalCommandsListed, ActionResolved, MovementResolved, ReactionResolved,
        )
    }
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
