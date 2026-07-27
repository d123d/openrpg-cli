"""Pure SRD 5.2.1 character progression projections."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from openrpg_cli.normalized import NormalizedRepository

XP_THRESHOLDS = (
    0,
    300,
    900,
    2700,
    6500,
    14000,
    23000,
    34000,
    48000,
    64000,
    85000,
    100000,
    120000,
    140000,
    165000,
    195000,
    225000,
    265000,
    305000,
    355000,
)
MULTICLASS_PREREQUISITES: Mapping[str, Mapping[str, int]] = MappingProxyType(
    {
        "barbarian": {"str": 13},
        "bard": {"cha": 13},
        "cleric": {"wis": 13},
        "druid": {"wis": 13},
        "fighter": {"str_or_dex": 13},
        "monk": {"dex": 13, "wis": 13},
        "paladin": {"str": 13, "cha": 13},
        "ranger": {"dex": 13, "wis": 13},
        "rogue": {"dex": 13},
        "sorcerer": {"cha": 13},
        "warlock": {"cha": 13},
        "wizard": {"int": 13},
    }
)


@dataclass(frozen=True, slots=True)
class FeatureGrant:
    feature_key: str
    item_key: str
    level: int


@dataclass(frozen=True, slots=True)
class ClassProgression:
    class_key: str
    subclass_keys: tuple[str, ...]
    levels: tuple[tuple[FeatureGrant, ...], ...]


def proficiency_bonus(total_level: int) -> int:
    if isinstance(total_level, bool) or not 1 <= total_level <= 20:
        raise ValueError("total_level: expected 1..20")
    return 2 + (total_level - 1) // 4


def level_for_xp(xp: int) -> int:
    if isinstance(xp, bool) or not isinstance(xp, int) or xp < 0:
        raise ValueError("xp: expected nonnegative integer")
    return max(i + 1 for i, threshold in enumerate(XP_THRESHOLDS) if xp >= threshold)


def validate_advancement(
    current: int, target: int, *, xp: int | None = None, milestone: bool = False
) -> None:
    if target != current + 1 or not 1 <= current < 20:
        raise ValueError("target_level: advancement must be one level")
    if milestone == (xp is not None):
        raise ValueError("advancement: choose exactly one of xp or milestone")
    if xp is not None and xp < XP_THRESHOLDS[target - 1]:
        raise ValueError("xp: below target threshold")


def _slug(key: str) -> str:
    return key.rsplit("_", 1)[-1]


def validate_multiclass(
    class_levels: Mapping[str, int], new_class: str, abilities: Mapping[str, int]
) -> Mapping[str, int]:
    if not class_levels or sum(class_levels.values()) >= 20:
        raise ValueError("class_levels: invalid total")
    slug = _slug(new_class)
    reqs = MULTICLASS_PREREQUISITES.get(slug)
    if reqs is None:
        raise ValueError("new_class: unknown base class")
    for ability, score in reqs.items():
        if ability == "str_or_dex":
            if max(abilities.get("str", 0), abilities.get("dex", 0)) < score:
                raise ValueError("abilities.str_or_dex: prerequisite unmet")
        elif abilities.get(ability, 0) < score:
            raise ValueError(f"abilities.{ability}: prerequisite unmet")
    out = dict(class_levels)
    out[new_class] = out.get(new_class, 0) + 1
    return MappingProxyType(out)


def build_progressions(repo: NormalizedRepository | None = None) -> Mapping[str, ClassProgression]:
    repo = repo or NormalizedRepository()
    classes = repo.load("CharacterClass.json")
    features = {x.pk: x for x in repo.load("ClassFeature.json")}
    items = repo.load("ClassFeatureItem.json")
    base = {x.pk: x for x in classes if x.data.get("subclass_of") is None}
    subclasses = {
        key: tuple(sorted(x.pk for x in classes if x.data.get("subclass_of") == key))
        for key in base
    }
    grants: dict[str, list[list[FeatureGrant]]] = {key: [[] for _ in range(20)] for key in base}
    for item in items:
        feature = features.get(item.parent)
        if feature is None:
            raise ValueError(f"{item.pk}: unknown feature parent")
        owner = str(feature.parent)
        if owner not in base:
            owner_entity = next((x for x in classes if x.pk == owner), None)
            if owner_entity is None or owner_entity.data.get("subclass_of") not in base:
                raise ValueError(f"{feature.pk}: unknown class owner")
            owner = str(owner_entity.data["subclass_of"])
        level = item.data.get("level")
        if isinstance(level, bool) or not isinstance(level, int) or not 1 <= level <= 20:
            raise ValueError(f"{item.pk}: invalid level")
        grants[owner][level - 1].append(FeatureGrant(feature.pk, item.pk, level))
    return MappingProxyType(
        {
            key: ClassProgression(
                key,
                subclasses[key],
                tuple(
                    tuple(sorted(level, key=lambda x: (x.level, x.feature_key, x.item_key)))
                    for level in grants[key]
                ),
            )
            for key in sorted(base)
        }
    )
