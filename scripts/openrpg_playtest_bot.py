"""Run bounded OpenRPG CLI combat playtests with heuristic or external AI control."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from openrpg_cli.api import get_rules_api  # noqa: E402
from openrpg_cli.character_builder import CharacterBuilder, CharacterRequest  # noqa: E402
from openrpg_cli.character_store import CharacterStore  # noqa: E402
from openrpg_cli.playtest_agent import CoverageController, SubprocessController  # noqa: E402
from openrpg_cli.playtest_bot import (  # noqa: E402
    PlaytestCase,
    run_playtest_matrix,
    write_matrix_artifacts,
    write_playtest_artifacts,
)


def _parse_seeds(value: str) -> tuple[int, ...]:
    try:
        seeds = tuple(int(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("seeds must be comma-separated integers") from exc
    if not seeds:
        raise argparse.ArgumentTypeError("at least one seed is required")
    return seeds


def _parse_csv(value: str) -> tuple[str, ...]:
    values = tuple(item.strip() for item in value.split(",") if item.strip())
    if not values:
        raise argparse.ArgumentTypeError("at least one value is required")
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character", type=Path)
    parser.add_argument("--monster", default="Goblin Warrior")
    parser.add_argument("--monsters", type=_parse_csv)
    parser.add_argument("--classes", type=_parse_csv, default=("Fighter",))
    parser.add_argument("--seeds", type=_parse_seeds, default=(42, 7, 11))
    parser.add_argument("--turns", type=int, default=200)
    parser.add_argument("--max-runs", type=int, default=256)
    parser.add_argument("--controller", nargs="+", help="External command implementing JSON stdio")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument(
        "--determinism-check",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Replay each deterministic case and compare mechanical fingerprints.",
    )
    parser.add_argument("--log-dir", type=Path, default=Path("playlogs/srd-playtest"))
    parser.add_argument("--report-dir", type=Path, default=Path("scores/playtest-bot"))
    args = parser.parse_args()

    api = get_rules_api()
    builder = CharacterBuilder(api)
    if args.character:
        characters = (CharacterStore(builder).load(args.character),)
    else:
        characters = tuple(
            builder.build(
                CharacterRequest(
                    f"SRD Bot {class_name}",
                    class_name,
                    "Human",
                    "Soldier",
                    "Savage Attacker",
                )
            )
            for class_name in args.classes
        )
    monster_names = args.monsters or (args.monster,)
    creatures = []
    for monster_name in monster_names:
        creature = api.get_creature(monster_name)
        if creature is None:
            parser.error(f"unknown or ambiguous creature: {monster_name}")
        creatures.append(creature)

    cases = tuple(
        PlaytestCase(character, creature, seed)
        for character in characters
        for creature in creatures
        for seed in args.seeds
    )
    def controller_factory():
        return (
            SubprocessController(args.controller, timeout=args.timeout)
            if args.controller
            else CoverageController()
        )

    matrix = run_playtest_matrix(
        cases,
        max_turns=args.turns,
        max_runs=args.max_runs,
        controller_factory=controller_factory,
        verify_determinism=args.determinism_check and not args.controller,
    )
    reports = []
    for report in matrix.runs:
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
    matrix_log, matrix_report = write_matrix_artifacts(
        matrix,
        log_dir=args.log_dir,
        report_dir=args.report_dir,
    )
    payload = {
        "ok": matrix.ok,
        "runs": reports,
        "outcome_coverage": matrix.outcome_coverage,
        "action_coverage": matrix.action_coverage,
        "interaction_coverage": matrix.interaction_coverage,
        "deterministic_failures": matrix.deterministic_failures,
        "matrix_log": str(matrix_log),
        "matrix_report": str(matrix_report),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if matrix.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
