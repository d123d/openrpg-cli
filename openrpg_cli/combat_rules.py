"""Combat-facing immutable SRD aggregate views."""

from __future__ import annotations
from dataclasses import dataclass
from openrpg_cli.data import normalize
from openrpg_cli.models import (
    Creature,
    CreatureAction,
    CreatureActionAttack,
    CreatureTrait,
    Weapon,
    WeaponProperty,
    WeaponPropertyAssignment,
)
from openrpg_cli.normalized import NormalizedRepository


@dataclass(frozen=True, slots=True)
class CreatureActionView:
    action: CreatureAction
    attacks: tuple[CreatureActionAttack, ...]


@dataclass(frozen=True, slots=True)
class CreatureView:
    entity: Creature
    traits: tuple[CreatureTrait, ...]
    actions: tuple[CreatureActionView, ...]


@dataclass(frozen=True, slots=True)
class WeaponPropertyView:
    assignment: WeaponPropertyAssignment
    property: WeaponProperty


@dataclass(frozen=True, slots=True)
class WeaponView:
    entity: Weapon
    properties: tuple[WeaponPropertyView, ...]


def _lookup(items, query):
    needle = normalize(query)
    hits = [
        x for x in items if normalize(x.entity.pk) == needle or normalize(x.entity.name) == needle
    ]
    return hits[0] if len(hits) == 1 else None


class CombatRules:
    def __init__(self, normalized: NormalizedRepository | None = None) -> None:
        n = normalized or NormalizedRepository()
        creatures = n.load("Creature.json")
        ci = {x.pk: x for x in creatures}
        traits = {}
        actions = {}
        action_rows = n.load("CreatureAction.json")
        ai = {x.pk: x for x in action_rows}
        attacks = {}
        for x in n.load("CreatureTrait.json"):
            if x.parent not in ci:
                raise ValueError(f"CreatureTrait.json/{x.pk}: orphan parent")
            traits.setdefault(x.parent, []).append(x)
        for x in action_rows:
            if x.parent not in ci:
                raise ValueError(f"CreatureAction.json/{x.pk}: orphan parent")
            actions.setdefault(x.parent, []).append(x)
        for x in n.load("CreatureActionAttack.json"):
            if x.parent not in ai:
                raise ValueError(f"CreatureActionAttack.json/{x.pk}: orphan parent")
            attacks.setdefault(x.parent, []).append(x)
        self.creatures = tuple(
            CreatureView(
                c,
                tuple(sorted(traits.get(c.pk, ()), key=lambda x: (x.name.casefold(), x.pk))),
                tuple(
                    CreatureActionView(
                        a,
                        tuple(
                            sorted(attacks.get(a.pk, ()), key=lambda x: (x.name.casefold(), x.pk))
                        ),
                    )
                    for a in sorted(
                        actions.get(c.pk, ()),
                        key=lambda x: (
                            x.data.get("order_in_statblock") or 0,
                            x.name.casefold(),
                            x.pk,
                        ),
                    )
                ),
            )
            for c in sorted(creatures, key=lambda x: (x.name.casefold(), x.pk))
        )
        weapons = n.load("Weapon.json")
        wi = {x.pk: x for x in weapons}
        props = n.load("WeaponProperty.json")
        pi = {x.pk: x for x in props}
        grouped = {}
        for x in n.load("WeaponPropertyAssignment.json"):
            if x.weapon not in wi or x.property not in pi:
                raise ValueError(f"WeaponPropertyAssignment.json/{x.pk}: orphan reference")
            grouped.setdefault(x.weapon, []).append(WeaponPropertyView(x, pi[x.property]))
        self.weapons = tuple(
            WeaponView(
                w,
                tuple(
                    sorted(
                        grouped.get(w.pk, ()),
                        key=lambda x: (
                            str(x.property.data.get("type") or ""),
                            x.property.name.casefold(),
                            x.property.pk,
                        ),
                    )
                ),
            )
            for w in sorted(weapons, key=lambda x: (x.name.casefold(), x.pk))
        )

    def get_creature(self, query: str):
        return _lookup(self.creatures, query)

    def get_weapon(self, query: str):
        return _lookup(self.weapons, query)
