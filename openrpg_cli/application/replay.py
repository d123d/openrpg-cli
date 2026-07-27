"""Verified genesis and snapshot replay."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from openrpg_cli.domain.codecs import canonical_json, decode_state
from openrpg_cli.domain.state import GameState
from openrpg_cli.engine.reducer import reduce_command
from openrpg_cli.engine.rng import DeterministicRNG

from .log import GENESIS_HASH, SessionLog


def state_hash(state: GameState) -> str:
    return hashlib.sha256(canonical_json(state)).hexdigest()


def event_hash(events: tuple) -> str:
    return hashlib.sha256(canonical_json(events)).hexdigest()


@dataclass(frozen=True, slots=True)
class Snapshot:
    position: int
    log_hash: str
    state_bytes: bytes
    state_hash: str
    rng: DeterministicRNG
    rng_hash: str
    schema_version: int = 1

    @classmethod
    def create(
        cls, position: int, log_hash: str, state: GameState, rng: DeterministicRNG
    ) -> "Snapshot":
        encoded = canonical_json(state)
        rng_hash = hashlib.sha256(canonical_json({"state": rng.state, "draws": rng.draws})).hexdigest()
        return cls(position, log_hash, encoded, hashlib.sha256(encoded).hexdigest(), rng, rng_hash)


def replay(
    genesis: GameState,
    initial_rng: DeterministicRNG,
    log: SessionLog,
    snapshot: Snapshot | None = None,
) -> tuple[GameState, DeterministicRNG]:
    log.validate()
    state, rng, start = genesis, initial_rng, 0
    if snapshot is not None:
        if snapshot.schema_version != 1 or snapshot.position < 0 or snapshot.position > len(log.records):
            raise ValueError("incompatible snapshot")
        anchor = GENESIS_HASH if snapshot.position == 0 else log.records[snapshot.position - 1].record_hash
        if snapshot.log_hash != anchor:
            raise ValueError("snapshot log anchor mismatch")
        if hashlib.sha256(snapshot.state_bytes).hexdigest() != snapshot.state_hash:
            raise ValueError("snapshot state hash mismatch")
        expected_rng = hashlib.sha256(
            canonical_json({"state": snapshot.rng.state, "draws": snapshot.rng.draws})
        ).hexdigest()
        if snapshot.rng_hash != expected_rng:
            raise ValueError("snapshot RNG hash mismatch")
        state, rng, start = decode_state(snapshot.state_bytes), snapshot.rng, snapshot.position
    for index, record in enumerate(log.records[start:], start):
        if rng != record.rng_before:
            raise ValueError(f"replay RNG mismatch at index {index}")
        result = reduce_command(state, record.command, rng)
        if result.events != record.events or result.rng != record.rng_after:
            raise ValueError(f"replay differential at index {index}")
        if state_hash(result.state) != record.state_hash:
            raise ValueError(f"replay state mismatch at index {index}")
        state, rng = result.state, result.rng
    return state, rng
