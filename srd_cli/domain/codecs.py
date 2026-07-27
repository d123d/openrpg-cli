"""Strict canonical JSON codecs for kernel values."""

from __future__ import annotations

import json
import math
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Any

from .messages import COMMAND_TYPES, EVENT_TYPES, Message
from .provenance import MAX_RUNTIME_BYTES, MAX_RUNTIME_DEPTH, RuntimeContentRef
from .state import (
    ActorState,
    ClockState,
    EffectState,
    EncounterState,
    GameState,
    ResourceState,
    SceneState,
    TeamState,
)

STATE_TYPES = {
    cls.__name__: cls
    for cls in (
        GameState,
        ActorState,
        TeamState,
        SceneState,
        EncounterState,
        ClockState,
        ResourceState,
        EffectState,
        RuntimeContentRef,
    )
}


def _plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        result = {f.name: _plain(getattr(value, f.name)) for f in fields(value)}
        result["type"] = value.type_tag if isinstance(value, Message) else value.__class__.__name__
        return result
    if isinstance(value, dict) or hasattr(value, "items"):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite number")
    return value


def canonical_json(value: Any) -> bytes:
    payload = json.dumps(
        _plain(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    if len(payload) > MAX_RUNTIME_BYTES:
        raise ValueError("payload exceeds maximum bytes")
    return payload


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _check_depth(value: Any, depth: int = 0) -> None:
    if depth > MAX_RUNTIME_DEPTH:
        raise ValueError("JSON exceeds maximum depth")
    if isinstance(value, dict):
        for child in value.values():
            _check_depth(child, depth + 1)
    elif isinstance(value, list):
        for child in value:
            _check_depth(child, depth + 1)


def parse_json(payload: bytes | str) -> dict[str, Any]:
    raw = payload.encode() if isinstance(payload, str) else payload
    if len(raw) > MAX_RUNTIME_BYTES:
        raise ValueError("payload exceeds maximum bytes")
    try:
        value = json.loads(raw, object_pairs_hook=_pairs, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"non-finite number: {x}")))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("kernel JSON root must be object")
    _check_depth(value)
    return value


def encode(value: Any) -> bytes:
    return canonical_json(value)


def decode_message(payload: bytes | str) -> Message:
    value = parse_json(payload)
    tag = value.pop("type", None)
    cls = COMMAND_TYPES.get(tag) or EVENT_TYPES.get(tag)
    if cls is None:
        raise ValueError(f"unknown message tag: {tag}")
    allowed = {f.name for f in fields(cls)}
    unknown = set(value) - allowed
    if unknown:
        raise ValueError(f"unknown message fields: {sorted(unknown)}")
    return cls(**value)


def _nested(cls: type, value: dict[str, Any]) -> Any:
    allowed = {f.name for f in fields(cls)}
    unknown = set(value) - allowed
    if unknown:
        raise ValueError(f"unknown {cls.__name__} fields: {sorted(unknown)}")
    if cls is SceneState and isinstance(value.get("runtime_content"), dict):
        value["runtime_content"] = RuntimeContentRef(**value["runtime_content"])
    return cls(**value)


def decode_state(payload: bytes | str) -> GameState:
    value = parse_json(payload)
    if value.pop("type", None) != "GameState":
        raise ValueError("expected GameState")
    allowed = {f.name for f in fields(GameState)}
    unknown = set(value) - allowed
    if unknown:
        raise ValueError(f"unknown GameState fields: {sorted(unknown)}")
    groups = {
        "actors": ActorState,
        "teams": TeamState,
        "scenes": SceneState,
        "encounters": EncounterState,
        "clocks": ClockState,
        "resources": ResourceState,
        "effects": EffectState,
    }
    for name, cls in groups.items():
        items = value.get(name, [])
        value[name] = tuple(_nested(cls, {k: v for k, v in item.items() if k != "type"}) for item in items)
    return GameState(**value)
