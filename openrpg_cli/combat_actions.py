"""Bounded adapters from structured SRD combat records."""

from __future__ import annotations

from dataclasses import dataclass

from openrpg_cli.combat_rules import CreatureView
from openrpg_cli.character_rules import SpellView


class UnsupportedCombatAction(ValueError):
    """Structured record cannot be resolved without inventing rules."""


@dataclass(frozen=True, slots=True)
class ResolvedAction:
    id: str
    name: str
    attack_bonus: int
    damage: str
    fallback: bool = False


class CombatActionCatalog:
    HALF_ON_SAVE = frozenset({"srd-2024_burning-hands", "srd-2024_thunderwave"})

    @classmethod
    def spell(cls, view: SpellView) -> ResolvedAction:
        row = view.spell
        data = row.data
        if (data.get("casting_time") != "action" or data.get("duration") != "instantaneous"
                or data.get("concentration") or data.get("target_count") != 1
                or data.get("shape_type") or not data.get("damage_roll")):
            raise UnsupportedCombatAction(f"{row.name}: unsupported combat mechanics")
        if not data.get("attack_roll") and not data.get("saving_throw_ability"):
            raise UnsupportedCombatAction(f"{row.name}: missing structured attack or save")
        return ResolvedAction(row.pk, row.name, 0, str(data["damage_roll"]))

    @staticmethod
    def enemy_actions(creature: CreatureView) -> tuple[ResolvedAction, ...]:
        found: list[ResolvedAction] = []
        for view in creature.actions:
            action = view.action
            if action.data.get("action_type") != "ACTION" or action.data.get("uses_type"):
                continue
            for attack in view.attacks:
                data = attack.data
                count, sides = data.get("damage_die_count"), data.get("damage_die_type")
                bonus, to_hit = data.get("damage_bonus"), data.get("to_hit_mod")
                if not isinstance(count, int) or not sides or not isinstance(to_hit, int):
                    continue
                expression = f"{count}d{str(sides).lstrip('Dd')}"
                if isinstance(bonus, int) and bonus:
                    expression += f"{bonus:+d}"
                extra_count, extra_sides = data.get("extra_damage_die_count"), data.get("extra_damage_die_type")
                if isinstance(extra_count, int) and extra_sides:
                    expression += f"+{extra_count}d{str(extra_sides).lstrip('Dd')}"
                    if isinstance(data.get("extra_damage_bonus"), int) and data["extra_damage_bonus"]:
                        expression += f"{data['extra_damage_bonus']:+d}"
                found.append(ResolvedAction(attack.pk, action.name, to_hit, expression))
        if found:
            return tuple(sorted(found, key=lambda x: (x.name.casefold(), x.id)))
        strength = int(creature.entity.data.get("ability_score_strength") or 10)
        modifier = (strength - 10) // 2
        return (ResolvedAction("fallback-unarmed", "Unarmed Strike", modifier, str(max(1, 1 + modifier)), True),)
