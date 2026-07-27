"""Character-facing immutable SRD aggregate views."""

from __future__ import annotations

from dataclasses import dataclass

from openrpg_cli.data import normalize
from openrpg_cli.models import (
    Background,
    BackgroundBenefit,
    CharacterClass,
    ClassFeature,
    ClassFeatureItem,
    Feat,
    FeatBenefit,
    Species,
    SpeciesTrait,
    Spell,
    SpellCastingOption,
)
from openrpg_cli.normalized import NormalizedRepository


@dataclass(frozen=True, slots=True)
class ClassFeatureView:
    feature: ClassFeature
    items: tuple[ClassFeatureItem, ...]


@dataclass(frozen=True, slots=True)
class SpellView:
    spell: Spell
    options: tuple[SpellCastingOption, ...]


@dataclass(frozen=True, slots=True)
class ClassView:
    entity: CharacterClass
    features: tuple[ClassFeatureView, ...]
    spells: tuple[SpellView, ...]
    parent: CharacterClass | None


@dataclass(frozen=True, slots=True)
class SpeciesView:
    entity: Species
    traits: tuple[SpeciesTrait, ...]
    parent: Species | None


@dataclass(frozen=True, slots=True)
class BackgroundView:
    entity: Background
    benefits: tuple[BackgroundBenefit, ...]


@dataclass(frozen=True, slots=True)
class FeatView:
    entity: Feat
    benefits: tuple[FeatBenefit, ...]


def _lookup(items: tuple, query: str):
    needle = normalize(query)
    matches = [
        item
        for item in items
        if normalize(item.entity.pk) == needle or normalize(item.entity.name) == needle
    ]
    return matches[0] if len(matches) == 1 else None


class CharacterRules:
    def __init__(self, normalized: NormalizedRepository | None = None) -> None:
        n = normalized or NormalizedRepository()
        classes = n.load("CharacterClass.json")
        class_idx = {item.pk: item for item in classes}
        features = n.load("ClassFeature.json")
        items = n.load("ClassFeatureItem.json")
        feature_idx = {item.pk: item for item in features}
        feature_items: dict[str, list[ClassFeatureItem]] = {}
        for item in items:
            if item.parent not in feature_idx:
                raise ValueError(f"ClassFeatureItem.json/{item.pk}: orphan parent {item.parent}")
            feature_items.setdefault(item.parent, []).append(item)
        by_class: dict[str, list[ClassFeature]] = {}
        for feature in features:
            if feature.parent not in class_idx:
                raise ValueError(f"ClassFeature.json/{feature.pk}: orphan parent {feature.parent}")
            by_class.setdefault(feature.parent, []).append(feature)
        options = n.load("SpellCastingOption.json")
        spells = n.load("Spell.json")
        spell_idx = {spell.pk: spell for spell in spells}
        by_spell: dict[str, list[SpellCastingOption]] = {}
        for option in options:
            if option.parent not in spell_idx:
                raise ValueError(
                    f"SpellCastingOption.json/{option.pk}: orphan parent {option.parent}"
                )
            by_spell.setdefault(option.parent, []).append(option)
        spell_views = {
            spell.pk: SpellView(
                spell,
                tuple(
                    sorted(
                        by_spell.get(spell.pk, ()),
                        key=lambda x: (str(x.data.get("type") or ""), x.pk),
                    )
                ),
            )
            for spell in spells
        }
        class_views: list[ClassView] = []
        for cls in classes:
            parent_pk = cls.data.get("subclass_of")
            if parent_pk is not None and parent_pk not in class_idx:
                raise ValueError(f"CharacterClass.json/{cls.pk}: orphan subclass {parent_pk}")
            feature_views = []
            for feature in by_class.get(cls.pk, ()):
                ordered_items = tuple(
                    sorted(
                        feature_items.get(feature.pk, ()),
                        key=lambda x: (x.data.get("level") or 0, x.pk),
                    )
                )
                feature_views.append(ClassFeatureView(feature, ordered_items))
            feature_views.sort(
                key=lambda x: (
                    min((i.data.get("level") or 0 for i in x.items), default=0),
                    x.feature.name.casefold(),
                    x.feature.pk,
                )
            )
            class_spells = [
                spell_views[spell.pk] for spell in spells if cls.pk in spell.data.get("classes", ())
            ]
            class_spells.sort(
                key=lambda x: (x.spell.data.get("level") or 0, x.spell.name.casefold(), x.spell.pk)
            )
            class_views.append(
                ClassView(cls, tuple(feature_views), tuple(class_spells), class_idx.get(parent_pk))
            )
        self.classes = tuple(
            sorted(class_views, key=lambda x: (x.entity.name.casefold(), x.entity.pk))
        )
        self.spells = tuple(
            sorted(
                spell_views.values(),
                key=lambda x: (x.spell.data.get("level") or 0, x.spell.name.casefold(), x.spell.pk),
            )
        )

        species = n.load("Species.json")
        species_idx = {x.pk: x for x in species}
        traits = n.load("SpeciesTrait.json")
        traits_by: dict[str, list[SpeciesTrait]] = {}
        for trait in traits:
            if trait.parent not in species_idx:
                raise ValueError(f"SpeciesTrait.json/{trait.pk}: orphan parent")
            traits_by.setdefault(trait.parent, []).append(trait)
        self.species = tuple(
            SpeciesView(
                s,
                tuple(
                    sorted(traits_by.get(s.pk, ()), key=lambda x: (x.data.get("order") or 0, x.pk))
                ),
                species_idx.get(s.data.get("subspecies_of")),
            )
            for s in species
        )
        self.backgrounds = self._benefit_views(
            n, "Background.json", "BackgroundBenefit.json", BackgroundView
        )
        self.feats = self._benefit_views(n, "Feat.json", "FeatBenefit.json", FeatView)

    @staticmethod
    def _benefit_views(n, parent_file, child_file, view_cls):
        parents = n.load(parent_file)
        idx = {x.pk: x for x in parents}
        grouped = {}
        for child in n.load(child_file):
            if child.parent not in idx:
                raise ValueError(f"{child_file}/{child.pk}: orphan parent")
            grouped.setdefault(child.parent, []).append(child)
        return tuple(
            view_cls(
                parent,
                tuple(
                    sorted(
                        grouped.get(parent.pk, ()),
                        key=lambda x: (str(x.data.get("type") or ""), x.name.casefold(), x.pk),
                    )
                ),
            )
            for parent in parents
        )

    def get_class(self, query: str):
        return _lookup(self.classes, query)

    def get_species(self, query: str):
        return _lookup(self.species, query)

    def get_background(self, query: str):
        return _lookup(self.backgrounds, query)

    def get_feat(self, query: str):
        return _lookup(self.feats, query)

    def get_spell(self, query: str):
        needle = normalize(query)
        hits = [
            x
            for x in self.spells
            if normalize(x.spell.pk) == needle or normalize(x.spell.name) == needle
        ]
        return hits[0] if len(hits) == 1 else None
