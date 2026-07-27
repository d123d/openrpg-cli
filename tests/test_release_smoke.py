import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from openrpg_cli.api import get_rules_api
from openrpg_cli.character_builder import CharacterBuilder, CharacterRequest
from openrpg_cli.combat_session import CombatSession


def test_release_command_surface():
    for args in (
        ["audit"],
        ["info"],
        ["roll", "1d6", "--seed", "1"],
        ["character", "--help"],
        ["combat", "--help"],
        ["play", "--help"],
        ["playtest", "--help"],
        ["dev", "--help"],
    ):
        result = subprocess.run(
            [sys.executable, "-m", "openrpg_cli", *args], text=True, capture_output=True, timeout=30
        )
        assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("monster", ["Goblin Warrior", "Ogre", "Air Elemental"])
def test_seeded_combat_cr_bands(monster):
    api = get_rules_api()
    hero = CharacterBuilder(api).build(
        CharacterRequest("Ada", "Fighter", "Human", "Soldier", "Savage Attacker")
    )
    result = CombatSession(hero, api.get_creature(monster), 41, api=api).run_auto()
    assert result.state.outcome.value in {"victory", "defeat"}


def test_isolated_wheel_contains_auditable_content_and_license(tmp_path):
    project = Path(__file__).resolve().parents[1]
    dist = tmp_path / "dist"
    subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(dist)],
        cwd=project,
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    target = tmp_path / "installed"
    wheel = next(dist.glob("*.whl"))
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--no-deps", "--target", str(target), str(wheel)],
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(target)
    audit = subprocess.run(
        [sys.executable, "-m", "openrpg_cli", "audit"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert audit.returncode == 0, audit.stderr
    pack_path = target / "openrpg_cli" / "data" / "providers" / "open5e" / "packs" / "srd521"
    manifest_path = pack_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["license"]["id"] == "CC-BY-4.0"
    assert manifest["source_document_ids"] == ["srd-2024"]
    assert (pack_path / "Creature.json").is_file()
    smoke = subprocess.run(
        [
            sys.executable,
            "-c",
            "from openrpg_cli.rules.resolution import *; from openrpg_cli.engine.rng import GameRNG; "
            "assert resolve_d20(D20Test(TestKind.CHECK), GameRNG(1))[1].draws == 1",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert smoke.returncode == 0, smoke.stderr
