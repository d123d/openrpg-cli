"""Combat orchestration and canonical serialization."""

from __future__ import annotations

import json
from dataclasses import dataclass

from srd_cli.character import Character
from srd_cli.combat import CombatEngine, CombatError, CombatEvent, CombatState, Outcome
from srd_cli.combat_rules import CreatureView
from srd_cli.api import RulesAPI


@dataclass(frozen=True, slots=True)
class CombatResult:
    seed: int
    state: CombatState
    events: tuple[CombatEvent, ...]


class CombatSession:
    def __init__(self, character: Character, creature: CreatureView, seed: int,
                 max_rounds: int = 100, api: RulesAPI | None = None) -> None:
        if not 1 <= max_rounds <= 10_000:
            raise CombatError("max rounds must be 1..10000")
        self.engine = CombatEngine(character, creature, seed, api)
        self.seed, self.max_rounds = seed, max_rounds
        self.kernel_state = None
        self.kernel_rng = None
        self.kernel_log = None

    def run_auto(self) -> CombatResult:
        while self.engine.state.outcome == Outcome.ACTIVE:
            if self.engine.state.round > self.max_rounds:
                raise CombatError(f"combat exceeded {self.max_rounds} rounds")
            actor = self.engine.state.active_actor
            action = self.engine.legal_player_actions()[0][1] if actor == "player" else None
            self.engine.act(actor, action)
        result = CombatResult(self.seed, self.engine.state, tuple(self.engine.events))
        # Import stays at interface boundary; legacy public output remains untouched.
        from srd_cli.interfaces.v1_compat import adapt_combat_result

        self.kernel_state, self.kernel_rng, self.kernel_log = adapt_combat_result(result)
        return result


def _payload(result: CombatResult) -> dict:
    return {
        "schema_version": 1,
        "seed": result.seed,
        "outcome": result.state.outcome.value,
        "rounds": result.state.round,
        "rng_draw_count": result.state.rng["draw_count"],
        "combatants": [
            {"id": x.id, "name": x.name, "hp": x.hp, "max_hp": x.max_hp,
             "armor_class": x.armor_class} for x in result.state.combatants
        ],
        "events": [{"kind": x.kind, "round": x.round, "actor": x.actor,
                    "payload": dict(x.payload)} for x in result.events],
    }


def render_combat_json(result: CombatResult) -> str:
    return json.dumps(_payload(result), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_transcript(result: CombatResult) -> str:
    lines = [f"Combat seed {result.seed}"]
    for event in result.events:
        if event.kind == "initiative":
            lines.append(f"R{event.round} {event.actor}: initiative {event.payload['total']}")
        else:
            p = event.payload
            verdict = (f"{p['damage']} damage, {p['hp']} HP"
                       if event.kind == "save_spell" or p["hit"] else "miss")
            lines.append(f"R{event.round} {event.actor}: {p['action']} -> {p['target']} ({verdict})")
    lines.append(f"Result: {result.state.outcome.value}")
    return "\n".join(lines) + "\n"
