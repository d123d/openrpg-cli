"""Feature-owned, ordered, idempotent recovery hooks."""

from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Callable
from .spellcasting import CastingState, Resource


@dataclass(frozen=True, slots=True)
class RestRequest:
    rest_id: str
    kind: str
    duration_minutes: int
    interrupted: bool = False


@dataclass(frozen=True, slots=True)
class RecoveryHook:
    id: str
    source_key: str
    cadence: str
    apply: Callable[[CastingState], CastingState]


@dataclass(frozen=True, slots=True)
class RestResult:
    completed: bool
    state: CastingState
    applied_hooks: tuple[str, ...]


def resource_recovery_hook(resource: Resource) -> RecoveryHook:
    def apply(state: CastingState) -> CastingState:
        return replace(
            state,
            resources=tuple(
                replace(r, current=r.maximum) if r.id == resource.id else r for r in state.resources
            ),
        )

    return RecoveryHook(resource.id, resource.source_key, resource.recharge, apply)


def perform_rest(
    request: RestRequest,
    state: CastingState,
    hooks: tuple[RecoveryHook, ...],
    already_completed: frozenset[str] = frozenset(),
) -> RestResult:
    if request.kind not in {"short", "long"}:
        raise ValueError("rest.kind: invalid")
    minimum = 60 if request.kind == "short" else 480
    if request.duration_minutes < minimum:
        raise ValueError("rest.duration: insufficient")
    if request.rest_id in already_completed:
        raise ValueError("rest.id: duplicate")
    if request.interrupted:
        return RestResult(False, state, ())
    out = state
    applied = []
    for hook in sorted(hooks, key=lambda x: (x.source_key, x.id)):
        if hook.cadence == request.kind or request.kind == "long" and hook.cadence == "short":
            out = hook.apply(out)
            applied.append(hook.id)
    if request.kind == "long":
        out = replace(out, slots=out.slot_maximum)
    return RestResult(True, out, tuple(applied))
