"""Deterministic typed read-only layer over bundled SRD tables."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, TypeVar

from srd_cli.data import SRDRepository, get_repository
from srd_cli.models import (
    Background,
    BackgroundBenefit,
    CharacterClass,
    ClassFeature,
    ClassFeatureItem,
    Creature,
    CreatureAction,
    CreatureActionAttack,
    CreatureTrait,
    Entity,
    Feat,
    FeatBenefit,
    Language,
    Relationship,
    Size,
    Species,
    SpeciesTrait,
    Spell,
    SpellCastingOption,
    SpellSchool,
    Weapon,
    WeaponProperty,
    WeaponPropertyAssignment,
    freeze,
)

T = TypeVar("T", bound=Entity)

MODELS: dict[str, type[Entity]] = {
    "CharacterClass.json": CharacterClass,
    "ClassFeature.json": ClassFeature,
    "ClassFeatureItem.json": ClassFeatureItem,
    "Species.json": Species,
    "SpeciesTrait.json": SpeciesTrait,
    "Background.json": Background,
    "BackgroundBenefit.json": BackgroundBenefit,
    "Feat.json": Feat,
    "FeatBenefit.json": FeatBenefit,
    "Creature.json": Creature,
    "CreatureTrait.json": CreatureTrait,
    "CreatureAction.json": CreatureAction,
    "CreatureActionAttack.json": CreatureActionAttack,
    "Weapon.json": Weapon,
    "WeaponProperty.json": WeaponProperty,
    "WeaponPropertyAssignment.json": WeaponPropertyAssignment,
    "Spell.json": Spell,
    "SpellCastingOption.json": SpellCastingOption,
    "Language.json": Language,
    "SpellSchool.json": SpellSchool,
    "Size.json": Size,
}

_ALL_TABLES = (
    "AbilityDescription.json",
    "AlignmentDescription.json",
    "Armor.json",
    "Background.json",
    "BackgroundBenefit.json",
    "CharacterClass.json",
    "ClassFeature.json",
    "ClassFeatureItem.json",
    "ConditionDescription.json",
    "Creature.json",
    "CreatureAction.json",
    "CreatureActionAttack.json",
    "CreatureTrait.json",
    "CreatureTypeDescription.json",
    "CrossReference.json",
    "DamageTypeDescription.json",
    "Document.json",
    "Feat.json",
    "FeatBenefit.json",
    "Item.json",
    "ItemCategory.json",
    "Language.json",
    "MagicItem.json",
    "Rule.json",
    "RuleSet.json",
    "Service.json",
    "Services.json",
    "Size.json",
    "SkillDescription.json",
    "Species.json",
    "SpeciesTrait.json",
    "Spell.json",
    "SpellCastingOption.json",
    "SpellSchool.json",
    "Weapon.json",
    "WeaponProperty.json",
    "WeaponPropertyAssignment.json",
)


@dataclass(frozen=True, slots=True)
class TableSpec:
    exposed: bool
    model: type[Entity] | None = None
    reason: str | None = None


TABLE_CATALOG: Mapping[str, TableSpec] = MappingProxyType(
    {
        name: TableSpec(
            name not in {"CrossReference.json", "Document.json"},
            MODELS.get(name),
            None
            if name not in {"CrossReference.json", "Document.json"}
            else "provenance/transform metadata",
        )
        for name in _ALL_TABLES
    }
)


class NormalizedRepository:
    def __init__(self, repository: SRDRepository | None = None) -> None:
        self.repository = repository or get_repository()
        declared = set((self.repository.manifest().get("declared_files") or {}))
        if declared != set(TABLE_CATALOG):
            raise ValueError("manifest tables do not match normalized table catalog")

    def load(self, filename: str) -> tuple[Entity, ...]:
        spec = TABLE_CATALOG.get(filename)
        if spec is None or spec.model is None:
            raise ValueError(f"{filename}: no typed model")
        result: list[Entity] = []
        seen: set[str] = set()
        for row in self.repository.table(filename):
            pk = str(row.get("pk") or "")
            if not pk:
                raise ValueError(f"{filename}: missing primary key")
            if pk in seen:
                raise ValueError(f"{filename}: duplicate primary key {pk}")
            seen.add(pk)
            fields = dict(row.get("fields") or {})
            name = str(fields.get("name") or pk)
            data = freeze(fields)
            cls = spec.model
            if issubclass(cls, Relationship):
                parent = fields.get("parent")
                if not isinstance(parent, str) or not parent:
                    raise ValueError(f"{filename}/{pk}: missing required parent")
                entity = cls(pk=pk, name=name, data=data, parent=parent)
            elif cls is WeaponPropertyAssignment:
                weapon, prop = fields.get("weapon"), fields.get("property")
                if not isinstance(weapon, str) or not isinstance(prop, str):
                    raise ValueError(f"{filename}/{pk}: missing weapon/property")
                entity = cls(pk=pk, name=name, data=data, weapon=weapon, property=prop)
            else:
                entity = cls(pk=pk, name=name, data=data)
            result.append(entity)
        return tuple(sorted(result, key=lambda item: str(item.pk)))

    def index(self, filename: str) -> Mapping[str, Entity]:
        return MappingProxyType({item.pk: item for item in self.load(filename)})

    def parent_index(self, filename: str) -> Mapping[str, tuple[Relationship, ...]]:
        grouped: dict[str, list[Relationship]] = {}
        for item in self.load(filename):
            if not isinstance(item, Relationship):
                raise ValueError(f"{filename}: rows have no parent")
            grouped.setdefault(item.parent, []).append(item)
        return MappingProxyType(
            {
                parent: tuple(sorted(items, key=lambda item: item.pk))
                for parent, items in grouped.items()
            }
        )
