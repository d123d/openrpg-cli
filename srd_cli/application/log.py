"""Bounded append-only hash-chained session history."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from srd_cli.domain.codecs import canonical_json
from srd_cli.domain.messages import Command, Event
from srd_cli.engine.rng import GameRNG

MAX_EVENTS_PER_RECORD = 1_000
MAX_RECORDS = 100_000
MAX_LOG_BYTES = 64_000_000
GENESIS_HASH = "0" * 64


@dataclass(frozen=True, slots=True)
class LogRecord:
    sequence: int
    command: Command
    events: tuple[Event, ...]
    rng_before: GameRNG
    rng_after: GameRNG
    state_hash: str
    previous_hash: str
    record_hash: str
    schema_version: int = 1

    def hash_material(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "sequence": self.sequence,
            "command": self.command,
            "events": self.events,
            "rng_before": {"state": self.rng_before.state, "draws": self.rng_before.draws},
            "rng_after": {"state": self.rng_after.state, "draws": self.rng_after.draws},
            "state_hash": self.state_hash,
            "previous_hash": self.previous_hash,
        }


@dataclass(frozen=True, slots=True)
class SessionLog:
    records: tuple[LogRecord, ...] = ()

    def append(
        self,
        command: Command,
        events: tuple[Event, ...],
        rng_before: GameRNG,
        rng_after: GameRNG,
        state_hash: str,
    ) -> "SessionLog":
        if len(self.records) >= MAX_RECORDS:
            raise ValueError("session record limit exceeded")
        if len(events) > MAX_EVENTS_PER_RECORD:
            raise ValueError("session event limit exceeded")
        previous = self.records[-1].record_hash if self.records else GENESIS_HASH
        provisional = LogRecord(
            len(self.records), command, tuple(events), rng_before, rng_after, state_hash, previous, ""
        )
        digest = hashlib.sha256(canonical_json(provisional.hash_material())).hexdigest()
        record = LogRecord(
            provisional.sequence,
            command,
            tuple(events),
            rng_before,
            rng_after,
            state_hash,
            previous,
            digest,
        )
        result = SessionLog(self.records + (record,))
        if result.encoded_size() > MAX_LOG_BYTES:
            raise ValueError("session byte limit exceeded")
        return result

    def encoded_size(self) -> int:
        return sum(len(canonical_json(r.hash_material())) for r in self.records)

    def validate(self) -> None:
        if len(self.records) > MAX_RECORDS or self.encoded_size() > MAX_LOG_BYTES:
            raise ValueError("session limits exceeded")
        previous = GENESIS_HASH
        for index, record in enumerate(self.records):
            if record.sequence != index or record.previous_hash != previous:
                raise ValueError(f"log chain invalid at index {index}")
            digest = hashlib.sha256(canonical_json(record.hash_material())).hexdigest()
            if digest != record.record_hash:
                raise ValueError(f"log record hash invalid at index {index}")
            previous = digest
