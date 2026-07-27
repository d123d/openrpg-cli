from __future__ import annotations

import json

from rich.console import Console

from openrpg_cli.api import get_rules_api
from openrpg_cli.character_builder import CharacterBuilder, CharacterRequest
from openrpg_cli.character_sheet import render_json, render_sheet


def character():
    return CharacterBuilder(get_rules_api()).build(CharacterRequest(
        "[bold]Ada[/bold]", "Wizard", "Human", "Sage", "Magic Initiate"))


def test_rich_sheet_is_complete_and_escaped():
    console = Console(record=True, width=48, color_system=None)
    char = character()
    render_sheet(char, console)
    text = console.export_text()
    for value in ("[bold]Ada[/bold]", "Wizard", "Human", "Sage", "Magic Initiate",
                  "STR", "Proficiency", "HP", "AC", "Saves", "Equipment", "Spells",
                  "Spellcasting"):
        assert value in text
    assert "EntityRef(" not in text


def test_json_is_complete_deterministic_and_pure():
    char = character()
    before = char
    one = render_json(char)
    assert one == render_json(char)
    data = json.loads(one)
    assert data["identity"]["class"]["name"] == "Wizard"
    assert data["derived"]["spell_save_dc"]
    assert {"scores", "equipment", "spells", "choices", "derived"} <= data.keys()
    assert char == before
