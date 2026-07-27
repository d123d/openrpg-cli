"""SRD condition hooks and context-neutral deterministic effect scheduler."""

from __future__ import annotations
from dataclasses import dataclass, replace
from enum import Enum


class Condition(str, Enum):
    BLINDED = "blinded"
    CHARMED = "charmed"
    DEAFENED = "deafened"
    EXHAUSTION = "exhaustion"
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


class Phase(str, Enum):
    START = "start"
    MAIN = "main"
    END = "end"


class DurationKind(str, Enum):
    MANUAL = "manual"
    FIXED = "fixed"
    PHASE_BOUND = "phase_bound"
    SAVE_ENDS = "save_ends"


@dataclass(frozen=True, slots=True)
class ConditionDefinition:
    condition: Condition
    srd_key: str
    implemented_hooks: tuple[str, ...]
    unsupported_clauses: tuple[str, ...] = ()


_HOOKS = {
    Condition.BLINDED: (
        "cannot_see",
        "sight_checks_auto_fail",
        "attacks_disadvantage",
        "attacks_against_advantage",
    ),
    Condition.CHARMED: ("cannot_attack_charmer", "charmer_social_advantage"),
    Condition.DEAFENED: ("cannot_hear", "hearing_checks_auto_fail"),
    Condition.EXHAUSTION: ("d20_penalty_by_level", "speed_reduction_by_level", "death_at_level_6"),
    Condition.FRIGHTENED: ("checks_attacks_disadvantage_while_visible", "cannot_move_closer"),
    Condition.GRAPPLED: ("speed_zero",),
    Condition.INCAPACITATED: ("no_actions", "no_reactions"),
    Condition.INVISIBLE: ("unseen", "attacks_advantage", "attacks_against_disadvantage"),
    Condition.PARALYZED: (
        "incapacitated",
        "speed_zero",
        "strength_dex_saves_auto_fail",
        "attacks_against_advantage",
        "nearby_hits_critical",
    ),
    Condition.PETRIFIED: (
        "incapacitated",
        "speed_zero",
        "strength_dex_saves_auto_fail",
        "damage_resistance",
        "poison_disease_immunity",
    ),
    Condition.POISONED: ("checks_attacks_disadvantage",),
    Condition.PRONE: (
        "crawl_only",
        "attacks_disadvantage",
        "nearby_attacks_advantage",
        "distant_attacks_disadvantage",
    ),
    Condition.RESTRAINED: (
        "speed_zero",
        "attacks_disadvantage",
        "attacks_against_advantage",
        "dex_saves_disadvantage",
    ),
    Condition.STUNNED: (
        "incapacitated",
        "speed_zero",
        "strength_dex_saves_auto_fail",
        "attacks_against_advantage",
    ),
    Condition.UNCONSCIOUS: (
        "incapacitated",
        "speed_zero",
        "unaware",
        "strength_dex_saves_auto_fail",
        "attacks_against_advantage",
        "nearby_hits_critical",
    ),
}
CONDITION_REGISTRY = {
    c: ConditionDefinition(c, f"srd-2024_{c.value}", hooks, ("prose_context_requires_caller",))
    for c, hooks in _HOOKS.items()
}


def exhaustion_hooks(level: int) -> tuple[str, ...]:
    if not 0 <= level <= 6:
        raise ValueError("invalid exhaustion level")
    return (
        ()
        if level == 0
        else (
            f"d20_penalty:{-2 * level}",
            f"speed_reduction:{5 * level}",
            *(("dead",) if level == 6 else ()),
        )
    )


@dataclass(frozen=True, slots=True)
class Effect:
    id: str
    source_id: str
    target_id: str
    condition: Condition
    start_tick: int
    start_phase: Phase = Phase.START
    duration: DurationKind = DurationKind.MANUAL
    end_tick: int | None = None
    end_phase: Phase | None = None
    stacks: bool = False
    srd_key: str = ""
    level: int = 0
    processed: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if (
            not self.id
            or not self.source_id
            or not self.target_id
            or not 0 <= self.start_tick <= 1_000_000_000
        ):
            raise ValueError("invalid effect")
        if self.end_tick is not None and self.end_tick < self.start_tick:
            raise ValueError("invalid duration")
        if self.condition is Condition.EXHAUSTION and not 0 <= self.level <= 6:
            raise ValueError("invalid exhaustion level")


@dataclass(frozen=True, slots=True)
class EffectTransition:
    id: str
    effect_id: str
    kind: str
    tick: int
    phase: Phase


def add_effect(effects: tuple[Effect, ...], effect: Effect) -> tuple[Effect, ...]:
    if len(effects) >= 1024:
        raise ValueError("too many effects")
    if any(e.id == effect.id for e in effects):
        raise ValueError("duplicate effect id")
    if not effect.stacks:
        effects = tuple(
            e
            for e in effects
            if not (e.target_id == effect.target_id and e.condition == effect.condition)
        )
    return tuple(sorted((*effects, effect), key=lambda e: e.id))


def remove_effect(effects: tuple[Effect, ...], effect_id: str) -> tuple[Effect, ...]:
    return tuple(e for e in effects if e.id != effect_id)


def advance(
    effects: tuple[Effect, ...], tick: int, phase: Phase
) -> tuple[tuple[Effect, ...], tuple[EffectTransition, ...]]:
    if not 0 <= tick <= 1_000_000_000 or not isinstance(phase, Phase):
        raise ValueError("invalid clock")
    kept = []
    transitions = []
    for effect in sorted(effects, key=lambda e: e.id):
        due_id = f"{effect.id}:{tick}:{phase.value}:due"
        expired = effect.end_tick is not None and (tick, list(Phase).index(phase)) >= (
            effect.end_tick,
            list(Phase).index(effect.end_phase or Phase.END),
        )
        processed = set(effect.processed)
        if tick >= effect.start_tick and due_id not in processed:
            transitions.append(EffectTransition(due_id, effect.id, "due", tick, phase))
            processed.add(due_id)
        if expired:
            expiry_id = f"{effect.id}:{tick}:{phase.value}:expired"
            if expiry_id not in processed:
                transitions.append(EffectTransition(expiry_id, effect.id, "expired", tick, phase))
        else:
            kept.append(replace(effect, processed=tuple(sorted(processed))))
    return tuple(kept), tuple(transitions)
