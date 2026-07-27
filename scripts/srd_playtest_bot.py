"""Run bounded SRD CLI combat playtests with heuristic or external AI control."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from srd_cli.api import get_rules_api  # noqa: E402
from srd_cli.character_builder import CharacterBuilder, CharacterRequest  # noqa: E402
from srd_cli.character_store import CharacterStore  # noqa: E402
from srd_cli.playtest_agent import CoverageController, SubprocessController  # noqa: E402
from srd_cli.playtest_bot import run_playtest, write_playtest_artifacts  # noqa: E402


def _parse_seeds(value: str) -> tuple[int, ...]:
    try:
        seeds = tuple(int(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("seeds must be comma-separated integers") from exc
    if not seeds:
        raise argparse.ArgumentTypeError("at least one seed is required")
    return seeds


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character", type=Path)
    parser.add_argument("--monster", default="Goblin Warrior")
    parser.add_argument("--seeds", type=_parse_seeds, default=(42, 7, 11))
    parser.add_argument("--turns", type=int, default=200)
    parser.add_argument("--controller", nargs="+", help="External command implementing JSON stdio")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--log-dir", type=Path, default=Path("playlogs/srd-playtest"))
    parser.add_argument("--report-dir", type=Path, default=Path("scores/playtest-bot"))
    args = parser.parse_args()

    api = get_rules_api()
    builder = CharacterBuilder(api)
    if args.character:
        character = CharacterStore(builder).load(args.character)
    else:
        character = builder.build(
            CharacterRequest("SRD Bot", "Fighter", "Human", "Soldier", "Savage Attacker")
        )
    creature = api.get_creature(args.monster)
    if creature is None:
        parser.error(f"unknown or ambiguous creature: {args.monster}")

    reports = []
    for seed in args.seeds:
        controller = (
            SubprocessController(args.controller, timeout=args.timeout)
            if args.controller
            else CoverageController()
        )
        report = run_playtest(
            character,
            creature,
            seed=seed,
            max_turns=args.turns,
            controller=controller,
        )
        log_path, report_path = write_playtest_artifacts(
            report,
            log_dir=args.log_dir,
            report_dir=args.report_dir,
        )
        reports.append({
            "run_id": report.run_id,
            "ok": report.ok,
            "outcome": report.outcome,
            "turns": report.turns,
            "log": str(log_path),
            "report": str(report_path),
        })
    print(json.dumps(reports, indent=2, sort_keys=True))
    return 0 if all(item["ok"] for item in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
