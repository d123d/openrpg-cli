"""Bounded autonomous combat runner with evidence-backed QA reports."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from srd_cli.character import Character
from srd_cli.combat import CombatEvent, Outcome
from srd_cli.combat_rules import CreatureView
from srd_cli.combat_session import CombatSession
from srd_cli.playtest_agent import (
    AgentAction,
    AgentController,
    AgentObservation,
    ControllerError,
    CoverageController,
)


@dataclass(frozen=True, slots=True)
class PlaytestFinding:
    severity: str
    code: str
    turn: int
    action: str
    observed: str
    expected: str


@dataclass(frozen=True, slots=True)
class PlaytestTurn:
    turn: int
    round: int
    actor: str
    action: str
    action_id: str
    action_source: str
    rationale: str
    outcome: str
    player_hp: int
    enemy_hp: int
    rng_draw_count: int
    events: tuple[dict[str, Any], ...]


@dataclass(frozen=True, slots=True)
class PlaytestReport:
    schema_version: int
    run_id: str
    ok: bool
    seed: int
    character: str
    creature: str
    controller: str
    turns: int
    rounds: int
    outcome: str
    controller_decisions: int
    fallback_decisions: int
    action_coverage: dict[str, int]
    findings: tuple[PlaytestFinding, ...] = ()
    transcript: tuple[PlaytestTurn, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return result or "unnamed"


def _event_payload(event: CombatEvent) -> dict[str, Any]:
    return {
        "kind": event.kind,
        "round": event.round,
        "actor": event.actor,
        "payload": dict(event.payload),
    }


def _combatants(session: CombatSession) -> tuple[Any, Any]:
    player = next(x for x in session.engine.state.combatants if x.id == "player")
    enemy = next(x for x in session.engine.state.combatants if x.id != "player")
    return player, enemy


def _legal_actions(session: CombatSession) -> tuple[dict[str, Any], ...]:
    result = []
    for index, (kind, identity) in enumerate(session.engine.legal_player_actions(), 1):
        if kind == "weapon":
            view = session.engine.api.get_weapon(identity)
            label = view.entity.name if view is not None else identity
        elif kind == "spell":
            view = session.engine.api.get_spell(identity)
            label = view.spell.name if view is not None else identity
        else:
            label = "Unarmed Strike"
        result.append({"index": index, "kind": kind, "id": identity, "label": label})
    return tuple(result)


def _resolve_action(requested: str, offered: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    needle = requested.strip().casefold()
    if needle.isdigit():
        index = int(needle)
        matches = [item for item in offered if item["index"] == index]
    else:
        matches = [
            item for item in offered
            if needle in {
                str(item["id"]).casefold(),
                str(item["label"]).casefold(),
                f"{item['kind']}:{item['id']}".casefold(),
            }
        ]
    if len(matches) != 1:
        raise ControllerError(f"action {requested!r} is not one offered legal action")
    return matches[0]


def _observation(
    session: CombatSession,
    *,
    run_id: str,
    turn: int,
    offered: tuple[dict[str, Any], ...],
    recent_actions: list[str],
) -> AgentObservation:
    state = session.engine.state
    player, enemy = _combatants(session)
    character = session.engine.character
    return AgentObservation(
        schema_version=1,
        run_id=run_id,
        turn=turn,
        combat={
            "seed": session.seed,
            "round": state.round,
            "active_actor": state.active_actor,
            "outcome": state.outcome.value,
            "rng_draw_count": state.rng["draw_count"],
            "player": {
                "name": player.name,
                "class": character.class_ref.name,
                "species": character.species_ref.name,
                "hp": player.hp,
                "max_hp": player.max_hp,
                "armor_class": player.armor_class,
            },
            "enemy": {
                "name": enemy.name,
                "hp": enemy.hp,
                "max_hp": enemy.max_hp,
                "armor_class": enemy.armor_class,
            },
        },
        legal_actions=offered,
        recent_actions=tuple(recent_actions[-12:]),
        recent_events=tuple(_event_payload(x) for x in session.engine.events[-8:]),
    )


def run_playtest(
    character: Character,
    creature: CreatureView,
    *,
    seed: int = 42,
    max_turns: int = 200,
    controller: AgentController | None = None,
) -> PlaytestReport:
    """Run one deterministic, bounded encounter using public controller state."""
    if not 1 <= max_turns <= 10_000:
        raise ValueError("max turns must be 1..10000")
    active_controller = controller or CoverageController()
    session = CombatSession(character, creature, seed, max_rounds=max_turns)
    run_id = f"{_slug(character.name)}-{_slug(creature.entity.name)}-seed-{seed}"
    transcript: list[PlaytestTurn] = []
    findings: list[PlaytestFinding] = []
    recent_actions: list[str] = []
    coverage: dict[str, int] = {}
    controller_decisions = 0
    fallback_decisions = 0

    for turn in range(1, max_turns + 1):
        state = session.engine.state
        if state.outcome != Outcome.ACTIVE:
            break
        actor = state.active_actor
        round_no = state.round
        selected_id = ""
        selected_label = ""
        source = "engine"
        rationale = ""
        events: tuple[CombatEvent, ...]
        before_state = (
            state.round,
            state.turn_index,
            tuple((item.id, item.hp) for item in state.combatants),
            state.outcome.value,
            state.rng["draw_count"],
        )
        try:
            if actor == "player":
                offered = _legal_actions(session)
                if not offered:
                    findings.append(PlaytestFinding(
                        "critical", "no-legal-actions", turn, "",
                        "Player turn exposed zero legal actions.",
                        "Every valid character has at least one legal action.",
                    ))
                    break
                observation = _observation(
                    session,
                    run_id=run_id,
                    turn=turn,
                    offered=offered,
                    recent_actions=recent_actions,
                )
                controller_decisions += 1
                try:
                    decision = AgentAction.parse(active_controller.decide(observation))
                    selected = _resolve_action(decision.action, offered)
                    source = decision.controller or active_controller.name
                    rationale = decision.rationale
                except Exception as exc:  # noqa: BLE001
                    selected = offered[0]
                    source = "deterministic-fallback"
                    fallback_decisions += 1
                    findings.append(PlaytestFinding(
                        "warning", "controller-fallback", turn, str(selected["id"]),
                        str(exc),
                        "Controller returns exactly one offered action; fallback preserves run.",
                    ))
                selected_id = str(selected["id"])
                selected_label = str(selected["label"])
                coverage[selected_id] = coverage.get(selected_id, 0) + 1
                recent_actions.append(selected_id)
                _, events = session.engine.act(actor, selected_id)
            else:
                before = len(session.engine.events)
                session.engine.act(actor)
                events = tuple(session.engine.events[before:])
                selected_id = str(events[-1].payload.get("action") or "") if events else ""
                selected_label = selected_id
        except Exception as exc:  # noqa: BLE001
            findings.append(PlaytestFinding(
                "critical", "engine-exception", turn, selected_id,
                f"{type(exc).__name__}: {exc}",
                "Legal turn resolves without exception.",
            ))
            break
        after = session.engine.state
        after_state = (
            after.round,
            after.turn_index,
            tuple((item.id, item.hp) for item in after.combatants),
            after.outcome.value,
            after.rng["draw_count"],
        )
        if after_state == before_state:
            findings.append(PlaytestFinding(
                "critical", "state-stall", turn, selected_id,
                "Legal action returned without changing turn, HP, outcome, or RNG state.",
                "Every resolved turn advances public mechanical state.",
            ))
            break
        player, enemy = _combatants(session)
        transcript.append(PlaytestTurn(
            turn=turn,
            round=round_no,
            actor=actor,
            action=selected_label,
            action_id=selected_id,
            action_source=source,
            rationale=rationale,
            outcome=after.outcome.value,
            player_hp=player.hp,
            enemy_hp=enemy.hp,
            rng_draw_count=after.rng["draw_count"],
            events=tuple(_event_payload(x) for x in events),
        ))

    final = session.engine.state
    if final.outcome == Outcome.ACTIVE and not any(
        item.severity == "critical" for item in findings
    ):
        findings.append(PlaytestFinding(
            "warning", "turn-limit", len(transcript), "",
            f"Encounter remained active after {len(transcript)} turns.",
            f"Encounter reaches terminal outcome within max_turns={max_turns}.",
        ))
    ok = final.outcome != Outcome.ACTIVE and not any(
        item.severity == "critical" for item in findings
    )
    return PlaytestReport(
        schema_version=1,
        run_id=run_id,
        ok=ok,
        seed=seed,
        character=character.name,
        creature=creature.entity.name,
        controller=active_controller.name,
        turns=len(transcript),
        rounds=final.round,
        outcome=final.outcome.value,
        controller_decisions=controller_decisions,
        fallback_decisions=fallback_decisions,
        action_coverage=dict(sorted(coverage.items())),
        findings=tuple(findings),
        transcript=tuple(transcript),
    )


def render_report_markdown(report: PlaytestReport) -> str:
    """Render concise evidence report suitable for defect triage."""
    lines = [
        f"# SRD CLI Playtest: {report.run_id}",
        "",
        f"- Status: {'PASS' if report.ok else 'INCONCLUSIVE/FAIL'}",
        f"- Controller: `{report.controller}`",
        f"- Seed: `{report.seed}`",
        f"- Result: `{report.outcome}` after {report.turns} turns / {report.rounds} rounds",
        f"- Controller fallback decisions: {report.fallback_decisions}",
        (
            "- Repro: "
            f"`py -3.14 scripts/srd_playtest_bot.py --monster "
            f"\"{report.creature}\" --seeds {report.seed}`"
        ),
        "",
        "## Action Coverage",
        "",
    ]
    if report.action_coverage:
        lines.extend(f"- `{key}`: {count}" for key, count in report.action_coverage.items())
    else:
        lines.append("- None")
    lines.extend(["", "## Findings", ""])
    if report.findings:
        for finding in report.findings:
            lines.extend([
                f"### {finding.severity.upper()} `{finding.code}` — turn {finding.turn}",
                "",
                f"- Action: `{finding.action}`",
                f"- Observed: {finding.observed}",
                f"- Expected: {finding.expected}",
                "",
            ])
    else:
        lines.append("- None.")
    lines.extend(["", "## Transcript", ""])
    for turn in report.transcript:
        lines.append(
            f"- T{turn.turn} R{turn.round} `{turn.actor}`: `{turn.action}` "
            f"→ {turn.outcome}; HP player={turn.player_hp}, enemy={turn.enemy_hp}; "
            f"RNG draws={turn.rng_draw_count}"
        )
    return "\n".join(lines).rstrip() + "\n"


def write_playtest_artifacts(
    report: PlaytestReport,
    *,
    log_dir: Path = Path("playlogs/srd-playtest"),
    report_dir: Path = Path("scores/playtest-bot"),
) -> tuple[Path, Path]:
    """Persist canonical JSON evidence and Markdown triage report."""
    log_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{report.run_id}.json"
    report_path = report_dir / f"{report.run_id}.md"
    log_path.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report_path.write_text(render_report_markdown(report), encoding="utf-8")
    return log_path, report_path
