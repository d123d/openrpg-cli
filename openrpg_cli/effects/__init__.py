"""Declarative effect DSL for SRD spells, creatures, and items.

Effects are frozen dataclasses that describe game mechanics without
executing them. The engine resolves effects through the existing
ApplyEffect/RemoveEffect command pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class TargetKind(str, Enum):
    SELF = "self"
    SINGLE = "single"
    ALL_ALLIES = "all_allies"
    ALL_ENEMIES = "all_enemies"
    AREA_CONE = "area_cone"
    AREA_SPHERE = "area_sphere"
    AREA_LINE = "area_line"
    AREA_CUBE = "area_cube"
    AREA_CYLINDER = "area_cylinder"


class DamageType(str, Enum):
    ACID = "acid"
    BLUDGEONING = "bludgeoning"
    COLD = "cold"
    FIRE = "fire"
    FORCE = "force"
    LIGHTNING = "lightning"
    NECROTIC = "necrotic"
    PIERCING = "piercing"
    POISON = "poison"
    PSYCHIC = "psychic"
    RADIANT = "radiant"
    SLASHING = "slashing"
    THUNDER = "thunder"


class SaveAbility(str, Enum):
    STR = "str"
    DEX = "dex"
    CON = "con"
    INT = "int"
    WIS = "wis"
    CHA = "cha"


class Condition(str, Enum):
    BLINDED = "blinded"
    CHARMED = "charmed"
    DEAFENED = "deafened"
    FRIGHTENED = "frightened"
    GRAPPLED = "grappled"
    INCAPACITATED = "incapacitated"
    INVISIBLE = "invisible"
    PARALYZED = "paralyzed"
    PETRIFIED = "petrified"
    POISONED = "poisoned"
    PRONE = "prone"
    RESTRAINED = "restrained"
    STUNNED = "stunned"
    UNCONSCIOUS = "unconscious"


class DurationKind(str, Enum):
    INSTANTANEOUS = "instantaneous"
    ROUNDS = "rounds"
    MINUTES = "minutes"
    HOURS = "hours"
    END_OF_NEXT_TURN = "end_of_next_turn"
    SAVES_END = "saves_end"
    CONCENTRATION = "concentration"
    PERMANENT = "permanent"


# === Effect Primitives ===


@dataclass(frozen=True)
class DamageEffect:
    dice: str  # e.g. "2d6"
    damage_type: DamageType
    modifier: int = 0

    def describe(self) -> str:
        return f"{self.dice}+{self.modifier} {self.damage_type.value}" if self.modifier else f"{self.dice} {self.damage_type.value}"


@dataclass(frozen=True)
class HealEffect:
    dice: str | None = None
    flat: int = 0
    modifier: int = 0


@dataclass(frozen=True)
class ConditionEffect:
    condition: Condition
    duration: DurationKind = DurationKind.INSTANTANEOUS
    duration_value: int | None = None  # rounds/minutes/hours


@dataclass(frozen=True)
class BuffEffect:
    armor_class: int = 0
    attack_bonus: int = 0
    save_bonus: int = 0
    damage_bonus: int = 0
    advantage_on: tuple[str, ...] = ()
    disadvantage_on: tuple[str, ...] = ()
    duration: DurationKind = DurationKind.INSTANTANEOUS
    duration_value: int | None = None


@dataclass(frozen=True)
class MoveEffect:
    distance: int = 0
    forced: bool = False
    speed_type: str = "walking"  # walking, flying, swimming, burrowing


@dataclass(frozen=True)
class SummonEffect:
    creature_id: str
    count: int = 1
    duration: DurationKind = DurationKind.MINUTES
    duration_value: int = 1


@dataclass(frozen=True)
class SpendEffect:
    resource: str  # "spell_slot", "rage", "ki", "channel_divinity", etc.
    level: int = 1


@dataclass(frozen=True)
class RechargeEffect:
    resource: str
    on_roll: int | None = None  # recharge on 5-6, etc.


# === Composite Effects ===


@dataclass(frozen=True)
class AttackEffect:
    attack_bonus: str | int = "spell_attack"  # flat, "spell_attack", "str_mod", etc.
    damage: DamageEffect | None = None
    extra_damage: tuple[DamageEffect, ...] = ()
    on_hit: tuple[Any, ...] = ()  # nested effects
    on_crit: tuple[Any, ...] = ()
    reach: int = 5


@dataclass(frozen=True)
class SaveEffect:
    ability: SaveAbility
    dc: str | int = "spell_dc"  # "spell_dc", "8 + prof + mod", or flat
    on_save: dict[str, tuple[Any, ...]] = field(default_factory=dict)
    # keys: "success", "failure", "critical_success", "critical_failure"


@dataclass(frozen=True)
class AreaEffect:
    shape: TargetKind
    size: int = 20  # feet
    effects: tuple[Any, ...] = ()


# === Top-Level Effect Envelope ===


@dataclass(frozen=True)
class Effect:
    kind: str  # 'attack', 'save', 'damage', 'heal', 'condition', 'buff', 'move', 'summon', 'spend', 'area'
    target: TargetKind = TargetKind.SINGLE
    params: Mapping[str, Any] = field(default_factory=dict)


# === Spell Adapter ===


@dataclass(frozen=True)
class SpellAdapter:
    name: str
    level: int
    school: str
    casting_time: str
    range: str
    components: tuple[str, ...] = ()
    duration: str = "Instantaneous"
    concentration: bool = False
    ritual: bool = False
    effects: tuple[Any, ...] = ()
    higher_levels: str = ""
    source: str = "srd-2024"


# === Creature Action Adapter ===


@dataclass(frozen=True)
class ActionAdapter:
    name: str
    action_type: str  # "action", "bonus_action", "reaction", "legendary", "lair"
    effects: tuple[Any, ...] = ()


@dataclass(frozen=True)
class CreatureAdapter:
    name: str
    size: str = "Medium"
    type: str = "humanoid"
    ac: int = 10
    hp: int = 10
    hit_dice: str = "1d8"
    speed: int = 30
    str_score: int = 10
    dex_score: int = 10
    con_score: int = 10
    int_score: int = 10
    wis_score: int = 10
    cha_score: int = 10
    senses: tuple[str, ...] = ()
    languages: tuple[str, ...] = ()
    cr: str = "0"
    xp: int = 0
    actions: tuple[ActionAdapter, ...] = ()
    traits: tuple[ActionAdapter, ...] = ()
    reactions: tuple[ActionAdapter, ...] = ()
    legendary_actions: tuple[ActionAdapter, ...] = ()
    source: str = "srd-2024"


# === Weapon Adapter ===


@dataclass(frozen=True)
class WeaponAdapter:
    name: str
    damage: str  # "1d8"
    damage_type: DamageType
    properties: tuple[str, ...] = ()
    weight: float = 0
    cost: str = ""
    category: str = "martial"  # "simple" or "martial"
    range_normal: int = 0  # 0 = melee
    range_long: int = 0
    versatile_damage: str | None = None
    source: str = "srd-2024"


# === Item Adapter ===


@dataclass(frozen=True)
class ItemAdapter:
    name: str
    category: str  # "weapon", "armor", "adventuring_gear", "tool", "magic_item"
    weight: float = 0
    cost: str = ""
    effects: tuple[Any, ...] = ()
    source: str = "srd-2024"
