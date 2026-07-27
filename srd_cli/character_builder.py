"""Deterministic level-1 SRD character builder."""

from __future__ import annotations

from dataclasses import dataclass
from difflib import get_close_matches
from math import floor
from typing import Iterable

from srd_cli.api import RulesAPI, get_rules_api
from srd_cli.combat_actions import CombatActionCatalog, UnsupportedCombatAction
from srd_cli.character import (
    ABILITIES,
    AbilityScores,
    AttackSummary,
    Character,
    ChoiceRecord,
    DerivedStats,
    EntityRef,
)

PRIMARY = {
    "barbarian": "str", "bard": "cha", "cleric": "wis", "druid": "wis",
    "fighter": "str", "monk": "dex", "paladin": "str", "ranger": "dex",
    "rogue": "dex", "sorcerer": "cha", "warlock": "cha", "wizard": "int",
}
CASTING = {
    "bard": "cha", "cleric": "wis", "druid": "wis", "paladin": "cha",
    "ranger": "wis", "sorcerer": "cha", "warlock": "cha", "wizard": "int",
}
SKILLS = {
    "Athletics": "str", "Acrobatics": "dex", "Sleight of Hand": "dex",
    "Stealth": "dex", "Arcana": "int", "History": "int",
    "Investigation": "int", "Nature": "int", "Religion": "int",
    "Animal Handling": "wis", "Insight": "wis", "Medicine": "wis",
    "Perception": "wis", "Survival": "wis", "Deception": "cha",
    "Intimidation": "cha", "Performance": "cha", "Persuasion": "cha",
}


class ChoiceError(ValueError):
    """Untrusted creation choice failed exact SRD validation."""

    def __init__(self, field: str, value: str, candidates: Iterable[str] = ()) -> None:
        safe = str(value)[:200]
        choices = tuple(sorted(set(candidates), key=str.casefold))
        matches = get_close_matches(safe, choices, n=5, cutoff=0.35)
        suffix = f"; candidates: {', '.join(matches)}" if matches else ""
        super().__init__(f"{field}: unknown or illegal value {safe!r}{suffix}")
        self.field = field
        self.value = safe
        self.candidates = tuple(matches)


@dataclass(frozen=True, slots=True)
class CharacterRequest:
    name: str
    class_identity: str
    species_identity: str
    background_identity: str
    feat_identity: str
    scores: AbilityScores | None = None
    equipment: tuple[str, ...] = ()
    spells: tuple[str, ...] = ()
    level: int = 1


def modifier(score: int) -> int:
    return floor((score - 10) / 2)


def _ref(entity) -> EntityRef:
    return EntityRef(entity.pk, entity.name)


class CharacterBuilder:
    """Build characters using only injected, read-only normalized SRD rules."""

    def __init__(self, api: RulesAPI | None = None) -> None:
        self.api = api or get_rules_api()
        self._class_views = tuple(x for x in self.api.list_classes() if x.parent is None)
        self._species_views = tuple(x for x in self.api.list_species() if x.parent is None)
        self._background_views = tuple(self.api.list_backgrounds())
        self._feat_views = tuple(x for x in self.api.list_feats() if x.entity.data.get("type") == "Origin")
        self.classes = tuple(_ref(x.entity) for x in self._class_views)
        self.species = tuple(_ref(x.entity) for x in self._species_views)
        self.backgrounds = tuple(_ref(x.entity) for x in self._background_views)
        self.feats = tuple(_ref(x.entity) for x in self._feat_views)

    def legal_equipment(self) -> tuple[EntityRef, ...]:
        return tuple(_ref(x.entity) for x in self.api.list_weapons())

    def legal_spells(self, class_identity: str) -> tuple[EntityRef, ...]:
        class_view = self._select("class", class_identity, self._class_views)
        return tuple(_ref(x.spell) for x in class_view.spells if x.spell.data.get("level") in (0, 1))

    @staticmethod
    def _select(field: str, identity: str, views):
        if not isinstance(identity, str) or not identity.strip() or len(identity) > 200:
            raise ChoiceError(field, str(identity), ())
        needle = identity.casefold()
        hits = [x for x in views if needle in (x.entity.pk.casefold(), x.entity.name.casefold())]
        if len(hits) != 1:
            names = [x.entity.name for x in views] + [x.entity.pk for x in views]
            raise ChoiceError(field, identity, names)
        return hits[0]

    @staticmethod
    def _default_scores(class_view) -> AbilityScores:
        name = class_view.entity.name.casefold()
        if name not in PRIMARY:
            raise ValueError(f"class {class_view.entity.pk}: no primary-ability adapter")
        priorities = [PRIMARY[name], *class_view.entity.data.get("saving_throws", ()), *ABILITIES]
        order = tuple(dict.fromkeys(priorities))
        assigned = dict(zip(order, (15, 14, 13, 12, 10, 8), strict=True))
        return AbilityScores.from_mapping(assigned)

    def _default_equipment_names(self, class_view) -> tuple[str, ...]:
        """Resolve option A from structured class feature records against item tables."""
        text = " ".join(
            str(view.feature.data.get("desc") or "")
            for view in class_view.features
            if view.feature.data.get("feature_type") == "CORE_TRAITS_TABLE"
        )
        option_a = text.split("(A)", 1)[-1].split("(B)", 1)[0]
        names = [x.entity.name for x in self.api.list_weapons()]
        names.extend(str(row["fields"]["name"]) for row in self.api.repository.table("Armor.json"))
        return tuple(name for name in names if name.casefold() in option_a.casefold())

    def _weapons(self, values: tuple[str, ...], class_view) -> tuple:
        legal = tuple(self.api.list_weapons())
        if not values:
            defaults = self._default_equipment_names(class_view)
            selected = [x for x in legal if x.entity.name in defaults]
            return tuple(sorted(selected, key=lambda x: (x.entity.name.casefold(), x.entity.pk)))
        result = []
        for value in values:
            view = self.api.get_weapon(value)
            if view is None:
                raise ChoiceError("equipment", value, [x.entity.name for x in legal])
            result.append(view)
        return tuple(sorted({x.entity.pk: x for x in result}.values(), key=lambda x: x.entity.name.casefold()))

    def _spells(self, values: tuple[str, ...], class_view) -> tuple:
        legal = tuple(x for x in class_view.spells if x.spell.data.get("level") in (0, 1))
        if not values:
            supported = []
            for view in legal:
                try:
                    CombatActionCatalog.spell(view)
                except UnsupportedCombatAction:
                    continue
                supported.append(view)
            return tuple(supported[:2])
        result = []
        allowed = {x.spell.pk: x for x in legal}
        for value in values:
            view = self.api.get_spell(value)
            if view is None or view.spell.pk not in allowed:
                raise ChoiceError("spells", value, [x.spell.name for x in legal])
            result.append(view)
        return tuple(sorted({x.spell.pk: x for x in result}.values(), key=lambda x: (x.spell.data.get("level"), x.spell.name.casefold())))

    def build(self, request: CharacterRequest) -> Character:
        if isinstance(request.level, bool) or not 1 <= request.level <= 20:
            raise ValueError("level: expected 1..20")
        class_view = self._select("class", request.class_identity, self._class_views)
        species = self._select("species", request.species_identity, self._species_views)
        background = self._select("background", request.background_identity, self._background_views)
        feat = self._select("feat", request.feat_identity, self._feat_views)
        scores = request.scores or self._default_scores(class_view)
        weapons = self._weapons(tuple(request.equipment), class_view)
        spells = self._spells(tuple(request.spells), class_view)
        mods = {key: modifier(value) for key, value in scores.items()}
        save_names = tuple(class_view.entity.data.get("saving_throws", ()))
        proficiency = 2 + (request.level - 1) // 4
        saves = {key: mods[key] + (proficiency if key in save_names else 0) for key in ABILITIES}
        skills = {name: mods[ability] for name, ability in SKILLS.items()}
        for benefit in background.benefits:
            if benefit.data.get("type") == "skill_proficiency":
                desc = str(benefit.data.get("desc") or "")
                for name, ability in SKILLS.items():
                    if name in desc:
                        skills[name] = mods[ability] + proficiency
        attacks = []
        for weapon in weapons:
            properties = {x.property.name for x in weapon.properties}
            ranged = not any(name in properties for name in ("Thrown", "Finesse")) and bool(
                weapon.entity.data.get("range")
            )
            ability = "dex" if ranged or "Finesse" in properties and mods["dex"] > mods["str"] else "str"
            bonus = mods[ability] + proficiency
            sign = f"+{mods[ability]}" if mods[ability] >= 0 else str(mods[ability])
            attacks.append(AttackSummary(_ref(weapon.entity), ability, bonus, f"{weapon.entity.data['damage_dice']}{sign} {weapon.entity.data['damage_type']}"))
        class_name = class_view.entity.name.casefold()
        casting = CASTING.get(class_name)
        spell_bonus = mods[casting] + proficiency if casting else None
        armor_class = 10 + mods["dex"]
        # Armor is derived from class starting package; explicit equipment currently
        # selects supported attack weapons without discarding worn starting armor.
        equipment_names = set(self._default_equipment_names(class_view))
        armor_rows = [
            row for row in self.api.repository.table("Armor.json")
            if str(row["fields"]["name"]) in equipment_names
            and str(row["fields"]["name"]).casefold() != "shield"
        ]
        if armor_rows:
            # Option text can match "Leather Armor" inside "Studded Leather
            # Armor"; selecting strongest matched body armor avoids substring
            # ambiguity while remaining within selected SRD package.
            armor = max(armor_rows, key=lambda row: int(row["fields"]["ac_base"]))["fields"]
            dex_bonus = mods["dex"] if armor.get("ac_add_dexmod") else 0
            cap = armor.get("ac_cap_dexmod")
            if isinstance(cap, int):
                dex_bonus = min(dex_bonus, cap)
            armor_class = int(armor["ac_base"]) + dex_bonus
        if "Shield" in equipment_names:
            armor_class += 2
        hit_die = int(str(class_view.entity.data["hit_dice"]).lstrip("Dd"))
        max_hp = hit_die + mods["con"] + (request.level - 1) * (hit_die // 2 + 1 + mods["con"])
        derived = DerivedStats(
            modifiers=mods,
            proficiency_bonus=proficiency,
            max_hp=max_hp,
            current_hp=max_hp,
            armor_class=armor_class,
            saves=saves,
            skills=skills,
            attacks=tuple(attacks),
            spellcasting_ability=casting,
            spell_attack_bonus=spell_bonus,
            spell_save_dc=8 + spell_bonus if spell_bonus is not None else None,
        )
        choices = (
            ChoiceRecord("class", (class_view.entity.pk,)),
            ChoiceRecord("species", (species.entity.pk,)),
            ChoiceRecord("background", (background.entity.pk,)),
            ChoiceRecord("feat", (feat.entity.pk,)),
        )
        return Character(
            request.name, _ref(class_view.entity), _ref(species.entity), _ref(background.entity),
            _ref(feat.entity), scores, tuple(_ref(x.entity) for x in weapons),
            tuple(_ref(x.spell) for x in spells), choices, derived, level=request.level,
        )
