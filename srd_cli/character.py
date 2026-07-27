"""Immutable level-1 character contracts."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

CHARACTER_SCHEMA_VERSION = 1
ABILITIES = ("str", "dex", "con", "int", "wis", "cha")


def _integer(value: object, path: str, low: int | None = None, high: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{path}: expected integer")
    if low is not None and value < low or high is not None and value > high:
        raise ValueError(f"{path}: expected {low}..{high}")
    return value


@dataclass(frozen=True, slots=True)
class AbilityScores:
    str: int
    dex: int
    con: int
    int: int
    wis: int
    cha: int

    def __post_init__(self) -> None:
        for key in ABILITIES:
            _integer(getattr(self, key), f"scores.{key}", 1, 30)

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]) -> "AbilityScores":
        unknown = sorted(set(values) - set(ABILITIES))
        missing = sorted(set(ABILITIES) - set(values))
        if unknown or missing:
            raise ValueError(f"scores: unknown={unknown}, missing={missing}")
        return cls(**{key: values[key] for key in ABILITIES})  # type: ignore[arg-type]

    def items(self) -> tuple[tuple[str, int], ...]:
        return tuple((key, getattr(self, key)) for key in ABILITIES)


@dataclass(frozen=True, slots=True)
class EntityRef:
    pk: str
    name: str

    def __post_init__(self) -> None:
        if not self.pk.strip() or not self.name.strip():
            raise ValueError("reference pk/name must not be blank")


@dataclass(frozen=True, slots=True)
class ChoiceRecord:
    field: str
    values: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AttackSummary:
    weapon: EntityRef
    ability: str
    attack_bonus: int
    damage: str


@dataclass(frozen=True, slots=True)
class DerivedStats:
    modifiers: Mapping[str, int]
    proficiency_bonus: int
    max_hp: int
    current_hp: int
    armor_class: int
    saves: Mapping[str, int]
    skills: Mapping[str, int]
    attacks: tuple[AttackSummary, ...] = ()
    spellcasting_ability: str | None = None
    spell_attack_bonus: int | None = None
    spell_save_dc: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "modifiers", MappingProxyType(dict(self.modifiers)))
        object.__setattr__(self, "saves", MappingProxyType(dict(self.saves)))
        object.__setattr__(self, "skills", MappingProxyType(dict(self.skills)))


@dataclass(frozen=True, slots=True)
class Character:
    name: str
    class_ref: EntityRef
    species_ref: EntityRef
    background_ref: EntityRef
    feat_ref: EntityRef
    scores: AbilityScores
    equipment: tuple[EntityRef, ...]
    spells: tuple[EntityRef, ...]
    choices: tuple[ChoiceRecord, ...]
    derived: DerivedStats
    level: int = 1
    schema_version: int = CHARACTER_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name: must not be blank")
        if len(self.name) > 200:
            raise ValueError("name: maximum length is 200")
        if isinstance(self.level, bool) or self.level != 1:
            raise ValueError("level: only level 1 is supported")
        if self.schema_version != CHARACTER_SCHEMA_VERSION:
            raise ValueError(f"schema_version: expected {CHARACTER_SCHEMA_VERSION}")
