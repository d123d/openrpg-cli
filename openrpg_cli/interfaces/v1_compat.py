"""One-way v1 combat result to kernel audit-log adapter."""

from __future__ import annotations

from typing import Any

from openrpg_cli.application.log import SessionLog
from openrpg_cli.application.replay import state_hash
from openrpg_cli.domain.messages import RecordLegacy
from openrpg_cli.domain.state import GameState
from openrpg_cli.engine.reducer import reduce_command
from openrpg_cli.engine.rng import DeterministicRNG


def adapt_combat_result(result: Any) -> tuple[GameState, DeterministicRNG, SessionLog]:
    """Copy legacy events into stable typed records without changing v1 objects."""
    aggregate = f"v1-combat:{result.seed}"
    state = GameState(
        aggregate,
        metadata={"provenance": "legacy-v1-adapter", "seed": result.seed},
    )
    rng = DeterministicRNG(int(result.seed))
    log = SessionLog()
    for index, legacy in enumerate(result.events):
        payload = {
            "kind": legacy.kind,
            "round": legacy.round,
            "actor": legacy.actor,
            "payload": dict(legacy.payload),
        }
        command = RecordLegacy(
            id=f"{aggregate}:{index}",
            aggregate_id=aggregate,
            payload=payload,
        )
        reduced = reduce_command(state, command, rng)
        log = log.append(command, reduced.events, rng, reduced.rng, state_hash(reduced.state))
        state, rng = reduced.state, reduced.rng
    return state, rng, log
