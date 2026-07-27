"""Allowlisted adjacent save migrations."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from openrpg_cli.domain.codecs import decode_state

Migration = Callable[[dict[str, Any]], dict[str, Any]]
MIGRATIONS: dict[tuple[int, int], Migration] = {}


def register_migration(source: int, target: int, fn: Migration) -> None:
    if target != source + 1 or (source, target) in MIGRATIONS:
        raise ValueError("migrations must be unique adjacent upgrades")
    MIGRATIONS[(source, target)] = fn


def migrate(payload: dict[str, Any], target_version: int = 1):
    current = int(payload.get("schema_version", 0))
    if current > target_version:
        raise ValueError("save downgrade is not supported")
    value = dict(payload)
    while current < target_version:
        fn = MIGRATIONS.get((current, current + 1))
        if fn is None:
            raise ValueError(f"missing migration {current}->{current + 1}")
        value = fn(dict(value))
        next_version = int(value.get("schema_version", -1))
        if next_version != current + 1:
            raise ValueError("migration did not advance exactly one version")
        current = next_version
    from openrpg_cli.domain.codecs import canonical_json

    return decode_state(canonical_json(value))
