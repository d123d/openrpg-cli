"""Deterministic immutable one-on-one combat engine."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Mapping

from srd_cli.character import Character
from srd_cli.combat_actions import CombatActionCatalog
from srd_cli.combat_rules import CreatureView
from srd_cli.dice import GameRNG, roll_d20, roll_damage_with_crit


class CombatError(ValueError):
    pass


class Outcome(str, Enum):
    ACTIVE = "active"
    VICTORY = "victory"
    DEFEAT = "defeat"


@dataclass(frozen=True, slots=True)
class Combatant:
    id: str
    name: str
    hp: int
    max_hp: int
    armor_class: int
    initiative_modifier: int
    conditions: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CombatEvent:
    kind: str
    round: int
    actor: str
    payload: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class CombatState:
    combatants: tuple[Combatant, ...]
    order: tuple[str, ...]
    turn_index: int
    round: int
    outcome: Outcome
    rng: Mapping[str, Any]

    @property
    def active_actor(self) -> str:
        return self.order[self.turn_index]


class CombatEngine:
    def __init__(self, character: Character, creature: CreatureView, seed: int) -> None:
        self.character, self.creature = character, creature
        self.rng = GameRNG(seed)
        player = Combatant("player", character.name, character.derived.current_hp,
                           character.derived.max_hp, character.derived.armor_class,
                           character.derived.modifiers["dex"])
        row = creature.entity
        enemy = Combatant(row.pk, row.name, int(row.data["hit_points"]), int(row.data["hit_points"]),
                          int(row.data["armor_class"]), int(row.data.get("initiative_bonus") or 0))
        rolls = {x.id: roll_d20(self.rng, x.initiative_modifier) for x in (player, enemy)}
        order = tuple(x.id for x in sorted((player, enemy),
            key=lambda x: (-rolls[x.id].total, -x.initiative_modifier, x.id)))
        self.state = CombatState((player, enemy), order, 0, 1, Outcome.ACTIVE, self.rng.to_dict())
        self.events = [CombatEvent("initiative", 1, x.id, {"natural": rolls[x.id].natural,
            "total": rolls[x.id].total}) for x in (player, enemy)]

    def legal_player_actions(self) -> tuple[tuple[str, str], ...]:
        return tuple(("weapon", x.weapon.pk) for x in sorted(
            self.character.derived.attacks, key=lambda x: (x.weapon.name.casefold(), x.weapon.pk)))

    def act(self, actor: str, action_id: str | None = None) -> tuple[CombatState, tuple[CombatEvent, ...]]:
        before = self.rng.snapshot()
        if self.state.outcome != Outcome.ACTIVE:
            raise CombatError("encounter is complete")
        if actor != self.state.active_actor:
            raise CombatError(f"{actor}: not active actor")
        try:
            if actor == "player":
                attacks = {x.weapon.pk: x for x in self.character.derived.attacks}
                if action_id not in attacks:
                    raise CombatError(f"unknown or unequipped weapon: {action_id}")
                attack = attacks[action_id]
                return self._attack(actor, self.state.order[1 if self.state.order[0] == actor else 0],
                                    attack.weapon.name, attack.attack_bonus, attack.damage.split()[0])
            actions = CombatActionCatalog.enemy_actions(self.creature)
            selected = actions[self.rng.randint(0, len(actions) - 1, "enemy-action")]
            return self._attack(actor, "player", selected.name, selected.attack_bonus,
                                selected.damage, selected.fallback)
        except Exception:
            self.rng.restore(before)
            raise

    def _attack(self, actor: str, target: str, name: str, bonus: int, damage_expr: str,
                fallback: bool = False) -> tuple[CombatState, tuple[CombatEvent, ...]]:
        target_obj = next(x for x in self.state.combatants if x.id == target)
        attack = roll_d20(self.rng, bonus)
        hit = not attack.is_nat1 and (attack.is_nat20 or attack.total >= target_obj.armor_class)
        damage = max(0, roll_damage_with_crit(self.rng, damage_expr, attack.is_nat20).total) if hit else 0
        hp = max(0, target_obj.hp - damage)
        updated = replace(target_obj, hp=hp)
        combatants = tuple(updated if x.id == target else x for x in self.state.combatants)
        outcome = Outcome.VICTORY if target != "player" and hp == 0 else (
            Outcome.DEFEAT if target == "player" and hp == 0 else Outcome.ACTIVE)
        event = CombatEvent("attack", self.state.round, actor, {"action": name, "target": target,
            "natural": attack.natural, "total": attack.total, "armor_class": target_obj.armor_class,
            "hit": hit, "critical": attack.is_nat20, "damage": damage, "hp": hp, "fallback": fallback})
        index, round_no = self.state.turn_index, self.state.round
        if outcome == Outcome.ACTIVE:
            index = (index + 1) % len(self.state.order)
            if index == 0:
                round_no += 1
        self.state = CombatState(combatants, self.state.order, index, round_no, outcome, self.rng.to_dict())
        self.events.append(event)
        return self.state, (event,)
