"""Pure Rich and JSON character sheet rendering."""

from __future__ import annotations

import json

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from srd_cli.character import ABILITIES, Character
from srd_cli.character_store import character_mapping


def _signed(value: int) -> str:
    return f"{value:+d}"


def render_sheet(character: Character, console: Console) -> None:
    identity = Table(show_header=False, box=None)
    identity.add_row("Level / Class", f"{character.level} / {character.class_ref.name}")
    identity.add_row("Species", character.species_ref.name)
    identity.add_row("Background / Feat", f"{character.background_ref.name} / {character.feat_ref.name}")
    abilities = Table("Ability", "Score", "Modifier", box=None)
    for key in ABILITIES:
        abilities.add_row(key.upper(), str(getattr(character.scores, key)), _signed(character.derived.modifiers[key]))
    defenses = Table(show_header=False, box=None)
    defenses.add_row("Proficiency", _signed(character.derived.proficiency_bonus))
    defenses.add_row("HP", f"{character.derived.current_hp}/{character.derived.max_hp}")
    defenses.add_row("AC", str(character.derived.armor_class))
    saves = Table("Saves", "Bonus", box=None)
    for key in ABILITIES:
        saves.add_row(key.upper(), _signed(character.derived.saves[key]))
    skills = Table("Skill", "Bonus", box=None)
    for name, value in sorted(character.derived.skills.items()):
        skills.add_row(name, _signed(value))
    details = Table(show_header=False, box=None)
    details.add_row("Equipment", ", ".join(x.name for x in character.equipment) or "None")
    details.add_row("Spells", ", ".join(x.name for x in character.spells) or "None")
    for attack in character.derived.attacks:
        details.add_row("Attack", f"{attack.weapon.name}: {_signed(attack.attack_bonus)}; {attack.damage}")
    if character.derived.spellcasting_ability:
        details.add_row("Spellcasting", character.derived.spellcasting_ability.upper())
        details.add_row("Spell Attack / Save DC", f"{_signed(character.derived.spell_attack_bonus or 0)} / {character.derived.spell_save_dc}")
    else:
        details.add_row("Spellcasting", "None")
    console.print(Panel(
        Group(identity, abilities, defenses, saves, skills, details),
        title=Text(character.name), border_style="cyan",
    ))


def render_json(character: Character) -> str:
    return json.dumps(character_mapping(character), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
