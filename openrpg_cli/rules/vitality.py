"""Pure vitality, damage, healing, and death lifecycle rules."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from openrpg_cli.engine.rng import GameRNG


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


@dataclass(frozen=True, slots=True)
class DamageInstance:
    amount: int
    damage_type: DamageType
    dice_amount: int = 0
    flat_amount: int = 0
    critical: bool = False

    def __post_init__(self) -> None:
        if type(self.amount) is not int or not 0 <= self.amount <= 1_000_000:
            raise ValueError("invalid damage amount")
        if self.dice_amount < 0 or self.flat_amount < 0:
            raise ValueError("invalid damage metadata")


@dataclass(frozen=True, slots=True)
class Defenses:
    immunities: frozenset[DamageType] = frozenset()
    resistances: frozenset[DamageType] = frozenset()
    vulnerabilities: frozenset[DamageType] = frozenset()


@dataclass(frozen=True, slots=True)
class Vitality:
    maximum_hp: int
    current_hp: int
    temporary_hp: int = 0
    death_successes: int = 0
    death_failures: int = 0
    stable: bool = False
    dead: bool = False
    defeated: bool = False

    def __post_init__(self) -> None:
        if not 1 <= self.maximum_hp <= 1_000_000 or not 0 <= self.current_hp <= self.maximum_hp:
            raise ValueError("invalid hit points")
        if (
            not 0 <= self.temporary_hp <= 1_000_000
            or not 0 <= self.death_successes <= 3
            or not 0 <= self.death_failures <= 3
        ):
            raise ValueError("invalid vitality counters")


@dataclass(frozen=True, slots=True)
class DamageTransition:
    damage_type: DamageType
    raw: int
    adjusted: int
    defense: str
    temp_absorbed: int
    hp_lost: int


@dataclass(frozen=True, slots=True)
class DamageResult:
    state: Vitality
    transitions: tuple[DamageTransition, ...]
    massive_damage: bool = False


def apply_damage(
    state: Vitality,
    instances: tuple[DamageInstance, ...],
    defenses: Defenses = Defenses(),
    *,
    critical_hit: bool = False,
    player: bool = True,
) -> DamageResult:
    if len(instances) > 64:
        raise ValueError("too many damage instances")
    current, temp, failures = state.current_hp, state.temporary_hp, state.death_failures
    transitions = []
    massive = False
    for item in instances:
        raw = item.amount + (item.dice_amount if item.critical else 0)
        defense = "none"
        adjusted = raw
        if item.damage_type in defenses.immunities:
            adjusted, defense = 0, "immunity"
        elif item.damage_type in defenses.resistances:
            adjusted, defense = raw // 2, "resistance"
        elif item.damage_type in defenses.vulnerabilities:
            adjusted, defense = raw * 2, "vulnerability"
        absorbed = min(temp, adjusted)
        temp -= absorbed
        remaining = adjusted - absorbed
        before = current
        current = max(0, current - remaining)
        overflow = max(0, remaining - before)
        if before == 0 and remaining:
            failures = min(3, failures + (2 if critical_hit else 1))
        if before > 0 and current == 0 and overflow >= state.maximum_hp:
            massive = True
        transitions.append(
            DamageTransition(item.damage_type, raw, adjusted, defense, absorbed, before - current)
        )
    dead = state.dead or massive or failures >= 3
    defeated = state.defeated or (not player and current == 0)
    return DamageResult(
        Vitality(
            state.maximum_hp,
            current,
            temp,
            state.death_successes,
            failures,
            False if current == 0 else state.stable,
            dead,
            defeated,
        ),
        tuple(transitions),
        massive,
    )


def apply_healing(state: Vitality, amount: int) -> Vitality:
    if type(amount) is not int or amount < 0:
        raise ValueError("invalid healing amount")
    hp = min(state.maximum_hp, state.current_hp + amount)
    revived = state.current_hp == 0 and hp > 0
    return Vitality(
        state.maximum_hp,
        hp,
        state.temporary_hp,
        0 if revived else state.death_successes,
        0 if revived else state.death_failures,
        False if revived else state.stable,
        state.dead,
        state.defeated,
    )


def apply_temporary_hp(state: Vitality, amount: int) -> Vitality:
    if type(amount) is not int or amount < 0:
        raise ValueError("invalid temporary hp")
    return Vitality(
        state.maximum_hp,
        state.current_hp,
        max(state.temporary_hp, amount),
        state.death_successes,
        state.death_failures,
        state.stable,
        state.dead,
        state.defeated,
    )


def death_save(state: Vitality, rng: GameRNG) -> tuple[Vitality, int, GameRNG]:
    if state.current_hp or state.dead or state.defeated:
        raise ValueError("death save unavailable")
    roll, rng = rng.die(20)
    successes, failures = state.death_successes, state.death_failures
    if roll == 20:
        return Vitality(state.maximum_hp, 1, state.temporary_hp), roll, rng
    if roll == 1:
        failures += 2
    elif roll >= 10:
        successes += 1
    else:
        failures += 1
    successes, failures = min(3, successes), min(3, failures)
    return (
        Vitality(
            state.maximum_hp,
            0,
            state.temporary_hp,
            successes,
            failures,
            successes >= 3,
            failures >= 3,
            state.defeated,
        ),
        roll,
        rng,
    )


def stabilize(state: Vitality) -> Vitality:
    return Vitality(
        state.maximum_hp,
        state.current_hp,
        state.temporary_hp,
        0,
        0,
        True,
        state.dead,
        state.defeated,
    )


def recover(state: Vitality) -> Vitality:
    if not state.stable or state.dead:
        raise ValueError("recovery unavailable")
    return Vitality(state.maximum_hp, 1, state.temporary_hp)
