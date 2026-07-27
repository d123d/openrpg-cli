"""Immutable normalized SRD entity contracts."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping


def freeze(value: Any) -> Any:
    """Recursively convert JSON containers to immutable equivalents."""
    if isinstance(value, dict):
        return MappingProxyType({key: freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(freeze(item) for item in value)
    return value


@dataclass(frozen=True, slots=True)
class Entity:
    pk: str
    name: str
    data: Mapping[str, Any]

    def __getattr__(self, name: str) -> Any:
        try:
            return self.data[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


@dataclass(frozen=True, slots=True)
class Relationship(Entity):
    parent: str


@dataclass(frozen=True, slots=True)
class CharacterClass(Entity):
    pass


@dataclass(frozen=True, slots=True)
class ClassFeature(Relationship):
    pass


@dataclass(frozen=True, slots=True)
class ClassFeatureItem(Relationship):
    pass


@dataclass(frozen=True, slots=True)
class Species(Entity):
    pass


@dataclass(frozen=True, slots=True)
class SpeciesTrait(Relationship):
    pass


@dataclass(frozen=True, slots=True)
class Background(Entity):
    pass


@dataclass(frozen=True, slots=True)
class BackgroundBenefit(Relationship):
    pass


@dataclass(frozen=True, slots=True)
class Feat(Entity):
    pass


@dataclass(frozen=True, slots=True)
class FeatBenefit(Relationship):
    pass


@dataclass(frozen=True, slots=True)
class Creature(Entity):
    pass


@dataclass(frozen=True, slots=True)
class CreatureTrait(Relationship):
    pass


@dataclass(frozen=True, slots=True)
class CreatureAction(Relationship):
    pass


@dataclass(frozen=True, slots=True)
class CreatureActionAttack(Relationship):
    pass


@dataclass(frozen=True, slots=True)
class Weapon(Entity):
    pass


@dataclass(frozen=True, slots=True)
class WeaponProperty(Entity):
    pass


@dataclass(frozen=True, slots=True)
class WeaponPropertyAssignment(Entity):
    weapon: str
    property: str


@dataclass(frozen=True, slots=True)
class Spell(Entity):
    pass


@dataclass(frozen=True, slots=True)
class SpellCastingOption(Relationship):
    pass
