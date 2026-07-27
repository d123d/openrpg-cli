"""Pure allowlisted command reducer."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable

from srd_cli.domain.messages import (
    AdvanceEffects,
    ApplyDamage,
    ApplyEffect,
    Command,
    CommandRejected,
    CreateGame,
    DieRolled,
    EntityPut,
    Event,
    GameCreated,
    LegacyRecorded,
    EffectsChanged,
    Heal,
    MakeDeathSave,
    PutEntity,
    RecordLegacy,
    Recover,
    RemoveEffect,
    ResolutionCompleted,
    ResolveTest,
    RollDie,
    Stabilize,
    VitalityChanged,
)
from srd_cli.domain.state import (
    ActorState,
    ClockState,
    EffectState,
    EncounterState,
    GameState,
    ResourceState,
    SceneState,
    TeamState,
)

from .rng import GameRNG
from srd_cli.rules.resolution import D20Test, Proficiency, TestKind, resolve_d20
from srd_cli.rules.vitality import (
    DamageInstance,
    DamageType,
    Defenses,
    Vitality,
    apply_damage,
    apply_healing,
    death_save,
    recover,
    stabilize,
)
from srd_cli.rules.effects import (
    Condition,
    DurationKind,
    Effect,
    Phase,
    add_effect,
    advance,
    remove_effect,
)
from srd_cli.domain.codecs import _plain


@dataclass(frozen=True, slots=True)
class ReductionResult:
    state: GameState
    events: tuple[Event, ...]
    rng: GameRNG


def _event(cls: type[Event], command: Command, payload: dict) -> Event:
    return cls(id=f"{command.id}:event", aggregate_id=command.aggregate_id, payload=payload)


def _create(state: GameState, cmd: CreateGame, rng: GameRNG) -> ReductionResult:
    if state.id != cmd.aggregate_id:
        raise ValueError("aggregate id mismatch")
    return ReductionResult(state, (_event(GameCreated, cmd, {"game_id": state.id}),), rng)


def _put(state: GameState, cmd: PutEntity, rng: GameRNG) -> ReductionResult:
    kind, entity_id = str(cmd.payload.get("kind", "")), str(cmd.payload.get("id", ""))
    data = cmd.payload.get("data", {})
    table = {
        "actor": ("actors", ActorState),
        "team": ("teams", TeamState),
        "scene": ("scenes", SceneState),
        "encounter": ("encounters", EncounterState),
        "clock": ("clocks", ClockState),
        "resource": ("resources", ResourceState),
        "effect": ("effects", EffectState),
    }
    if kind not in table or not entity_id:
        raise ValueError("invalid entity kind or id")
    field, cls = table[kind]
    entity = cls(id=entity_id, data=data)
    current = getattr(state, field)
    updated = tuple(entity if x.id == entity_id else x for x in current)
    if not any(x.id == entity_id for x in current):
        updated += (entity,)
    return ReductionResult(
        replace(state, **{field: updated}),
        (_event(EntityPut, cmd, {"kind": kind, "id": entity_id}),),
        rng,
    )


def _roll(state: GameState, cmd: RollDie, rng: GameRNG) -> ReductionResult:
    sides = int(cmd.payload.get("sides", 0))
    value, next_rng = rng.die(sides)
    return ReductionResult(
        state, (_event(DieRolled, cmd, {"sides": sides, "result": value}),), next_rng
    )


def _legacy(state: GameState, cmd: RecordLegacy, rng: GameRNG) -> ReductionResult:
    return ReductionResult(state, (_event(LegacyRecorded, cmd, dict(cmd.payload)),), rng)


def _actor(state: GameState, actor_id: str) -> tuple[int, ActorState]:
    for index, actor in enumerate(state.actors):
        if actor.id == actor_id:
            return index, actor
    raise ValueError("unknown actor")


def _replace_actor(state: GameState, index: int, actor: ActorState, **data: object) -> GameState:
    actors = list(state.actors)
    actors[index] = replace(actor, data={**dict(actor.data), **data})
    return replace(state, actors=tuple(actors))


def _resolve(state: GameState, cmd: ResolveTest, rng: GameRNG) -> ReductionResult:
    p = dict(cmd.payload)
    test = D20Test(
        TestKind(p["kind"]),
        int(p.get("ability_modifier", 0)),
        int(p.get("proficiency_bonus", 0)),
        Proficiency(p.get("proficiency", "none")),
        tuple(p.get("circumstantial_modifiers", ())),
        tuple(p.get("advantage_sources", ())),
        tuple(p.get("disadvantage_sources", ())),
        p.get("target"),
        str(p.get("srd_key", "")),
    )
    result, rng = resolve_d20(test, rng)
    return ReductionResult(state, (_event(ResolutionCompleted, cmd, _plain(result)),), rng)


def _vitality_from(data: object) -> Vitality:
    if not isinstance(data, dict) and not hasattr(data, "items"):
        raise ValueError("missing vitality state")
    return Vitality(**dict(data))


def _damage(state: GameState, cmd: ApplyDamage, rng: GameRNG) -> ReductionResult:
    p = dict(cmd.payload)
    index, actor = _actor(state, str(p["actor_id"]))
    vitality = _vitality_from(actor.data.get("vitality"))
    instances = tuple(
        DamageInstance(int(x["amount"]), DamageType(x["damage_type"])) for x in p["instances"]
    )
    result = apply_damage(vitality, instances, Defenses(), player=bool(p.get("player", True)))
    state = _replace_actor(state, index, actor, vitality=_plain(result.state))
    return ReductionResult(state, (_event(VitalityChanged, cmd, _plain(result)),), rng)


def _heal(state: GameState, cmd: Heal, rng: GameRNG) -> ReductionResult:
    p = dict(cmd.payload)
    index, actor = _actor(state, str(p["actor_id"]))
    vitality = apply_healing(_vitality_from(actor.data.get("vitality")), int(p["amount"]))
    state = _replace_actor(state, index, actor, vitality=_plain(vitality))
    return ReductionResult(state, (_event(VitalityChanged, cmd, {"state": _plain(vitality)}),), rng)


def _death_op(state: GameState, cmd: Command, rng: GameRNG) -> ReductionResult:
    p = dict(cmd.payload)
    index, actor = _actor(state, str(p["actor_id"]))
    vitality = _vitality_from(actor.data.get("vitality"))
    if isinstance(cmd, MakeDeathSave):
        vitality, roll, rng = death_save(vitality, rng)
        extra = {"roll": roll}
    elif isinstance(cmd, Stabilize):
        vitality, extra = stabilize(vitality), {}
    else:
        vitality, extra = recover(vitality), {}
    state = _replace_actor(state, index, actor, vitality=_plain(vitality))
    return ReductionResult(
        state, (_event(VitalityChanged, cmd, {"state": _plain(vitality), **extra}),), rng
    )


def _effect(state: GameState, cmd: Command, rng: GameRNG) -> ReductionResult:
    effects = tuple(
        Effect(
            e.id,
            e.source_id or "",
            str(e.data["target_id"]),
            Condition(e.data["condition"]),
            int(e.data["start_tick"]),
            Phase(e.data.get("start_phase", "start")),
            DurationKind(e.data.get("duration", "manual")),
            e.data.get("end_tick"),
            Phase(e.data["end_phase"]) if e.data.get("end_phase") else None,
            bool(e.data.get("stacks", False)),
            str(e.data.get("srd_key", "")),
            int(e.data.get("level", 0)),
            tuple(e.data.get("processed", ())),
        )
        for e in state.effects
    )
    p = dict(cmd.payload)
    transitions = ()
    if isinstance(cmd, ApplyEffect):
        item = Effect(
            str(p["id"]),
            str(p["source_id"]),
            str(p["target_id"]),
            Condition(p["condition"]),
            int(p["start_tick"]),
            Phase(p.get("start_phase", "start")),
            DurationKind(p.get("duration", "manual")),
            p.get("end_tick"),
            Phase(p["end_phase"]) if p.get("end_phase") else None,
            bool(p.get("stacks", False)),
            str(p.get("srd_key", "")),
            int(p.get("level", 0)),
        )
        effects = add_effect(effects, item)
    elif isinstance(cmd, RemoveEffect):
        effects = remove_effect(effects, str(p["effect_id"]))
    else:
        effects, transitions = advance(effects, int(p["tick"]), Phase(p["phase"]))
    stored = tuple(
        EffectState(
            id=e.id,
            source_id=e.source_id,
            data={k: v for k, v in _plain(e).items() if k not in {"id", "source_id"}},
        )
        for e in effects
    )
    state = replace(state, effects=stored)
    return ReductionResult(
        state, (_event(EffectsChanged, cmd, {"transitions": _plain(transitions)}),), rng
    )


Handler = Callable[[GameState, Command, GameRNG], ReductionResult]
HANDLERS: dict[type, Handler] = {
    CreateGame: _create,
    PutEntity: _put,
    RollDie: _roll,
    RecordLegacy: _legacy,
    ResolveTest: _resolve,
    ApplyDamage: _damage,
    Heal: _heal,
    MakeDeathSave: _death_op,
    Stabilize: _death_op,
    Recover: _death_op,
    ApplyEffect: _effect,
    RemoveEffect: _effect,
    AdvanceEffects: _effect,
}


def reduce_command(state: GameState, command: Command, rng: GameRNG) -> ReductionResult:
    handler = HANDLERS.get(type(command))
    try:
        if handler is None:
            raise ValueError("unknown command type")
        return handler(state, command, rng)
    except (ValueError, TypeError, KeyError) as exc:
        event = CommandRejected(
            id=f"{command.id}:rejected",
            aggregate_id=command.aggregate_id,
            payload={"command_type": command.type_tag, "reason": str(exc)},
        )
        return ReductionResult(state, (event,), rng)
