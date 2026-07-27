"""Effect resolver — bridges declarative effects to engine commands.

Translates SpellAdapter/ActionAdapter/WeaponAdapter effects into
ApplyEffect, ApplyDamage, Heal, and other commands that the engine
already knows how to process.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openrpg_cli.effects import (
    AttackEffect, BuffEffect, ConditionEffect, DamageEffect, HealEffect,
    SaveEffect, SpellAdapter, ActionAdapter, WeaponAdapter, CreatureAdapter,
    TargetKind, DurationKind, Condition, SaveAbility,
)


@dataclass(frozen=True)
class ResolvedEffect:
    """An effect ready to become an engine command."""
    kind: str  # "damage", "heal", "condition", "buff", "attack", "save"
    target_id: str
    source_id: str
    params: dict[str, Any]


def resolve_attack(
    effect: AttackEffect,
    attacker_id: str,
    target_id: str,
) -> list[ResolvedEffect]:
    """Resolve an attack effect to damage/condition commands."""
    results = []
    if effect.damage:
        results.append(ResolvedEffect(
            kind="damage",
            target_id=target_id,
            source_id=attacker_id,
            params={
                "dice": effect.damage.dice,
                "damage_type": effect.damage.damage_type.value,
                "modifier": effect.damage.modifier,
            },
        ))
    for extra in effect.extra_damage:
        results.append(ResolvedEffect(
            kind="damage",
            target_id=target_id,
            source_id=attacker_id,
            params={
                "dice": extra.dice,
                "damage_type": extra.damage_type.value,
                "modifier": extra.modifier,
            },
        ))
    return results


def resolve_save(
    effect: SaveEffect,
    target_id: str,
    source_id: str,
    succeeded: bool,
    critical: bool = False,
) -> list[ResolvedEffect]:
    """Resolve a save effect based on outcome."""
    results = []
    if critical:
        key = "critical_success" if succeeded else "critical_failure"
    else:
        key = "success" if succeeded else "failure"

    for sub_effect in effect.on_save.get(key, ()):
        if isinstance(sub_effect, DamageEffect):
            results.append(ResolvedEffect(
                kind="damage",
                target_id=target_id,
                source_id=source_id,
                params={
                    "dice": sub_effect.dice,
                    "damage_type": sub_effect.damage_type.value,
                    "modifier": sub_effect.modifier,
                },
            ))
        elif isinstance(sub_effect, ConditionEffect):
            results.append(ResolvedEffect(
                kind="condition",
                target_id=target_id,
                source_id=source_id,
                params={
                    "condition": sub_effect.condition.value,
                    "duration": sub_effect.duration.value,
                    "duration_value": sub_effect.duration_value,
                },
            ))
    return results


def resolve_buff(
    effect: BuffEffect,
    target_id: str,
    source_id: str,
) -> list[ResolvedEffect]:
    """Resolve a buff effect."""
    return [ResolvedEffect(
        kind="buff",
        target_id=target_id,
        source_id=source_id,
        params={
            "armor_class": effect.armor_class,
            "attack_bonus": effect.attack_bonus,
            "save_bonus": effect.save_bonus,
            "damage_bonus": effect.damage_bonus,
            "duration": effect.duration.value,
            "duration_value": effect.duration_value,
        },
    )]


def resolve_heal(
    effect: HealEffect,
    target_id: str,
    source_id: str,
) -> list[ResolvedEffect]:
    """Resolve a heal effect."""
    return [ResolvedEffect(
        kind="heal",
        target_id=target_id,
        source_id=source_id,
        params={
            "dice": effect.dice,
            "flat": effect.flat,
            "modifier": effect.modifier,
        },
    )]


def resolve_condition(
    effect: ConditionEffect,
    target_id: str,
    source_id: str,
) -> list[ResolvedEffect]:
    """Resolve a condition effect."""
    return [ResolvedEffect(
        kind="condition",
        target_id=target_id,
        source_id=source_id,
        params={
            "condition": effect.condition.value,
            "duration": effect.duration.value,
            "duration_value": effect.duration_value,
        },
    )]


def resolve_spell(
    spell: SpellAdapter,
    caster_id: str,
    target_id: str,
) -> list[ResolvedEffect]:
    """Resolve all effects of a spell."""
    results = []
    for effect in spell.effects:
        if isinstance(effect, AttackEffect):
            results.extend(resolve_attack(effect, caster_id, target_id))
        elif isinstance(effect, SaveEffect):
            # Save effects need the save result; return as pending
            results.append(ResolvedEffect(
                kind="save_pending",
                target_id=target_id,
                source_id=caster_id,
                params={
                    "ability": effect.ability.value,
                    "dc": effect.dc,
                },
            ))
        elif isinstance(effect, BuffEffect):
            results.extend(resolve_buff(effect, caster_id if spell.range == "Self" else target_id, caster_id))
        elif isinstance(effect, HealEffect):
            results.extend(resolve_heal(effect, target_id, caster_id))
        elif isinstance(effect, ConditionEffect):
            results.extend(resolve_condition(effect, target_id, caster_id))
    return results


def resolve_creature_action(
    action: ActionAdapter,
    creature_id: str,
    target_id: str,
) -> list[ResolvedEffect]:
    """Resolve all effects of a creature action."""
    results = []
    for effect in action.effects:
        if isinstance(effect, AttackEffect):
            results.extend(resolve_attack(effect, creature_id, target_id))
        elif isinstance(effect, SaveEffect):
            results.append(ResolvedEffect(
                kind="save_pending",
                target_id=target_id,
                source_id=creature_id,
                params={
                    "ability": effect.ability.value,
                    "dc": effect.dc,
                },
            ))
        elif isinstance(effect, ConditionEffect):
            results.extend(resolve_condition(effect, target_id, creature_id))
    return results


def resolve_weapon_attack(
    weapon: WeaponAdapter,
    attacker_id: str,
    target_id: str,
    modifier: int = 0,
) -> list[ResolvedEffect]:
    """Resolve a weapon attack."""
    return [ResolvedEffect(
        kind="attack_pending",
        target_id=target_id,
        source_id=attacker_id,
        params={
            "weapon": weapon.name,
            "damage_dice": weapon.damage,
            "damage_type": weapon.damage_type.value,
            "modifier": modifier,
            "versatile_damage": weapon.versatile_damage,
        },
    )]
