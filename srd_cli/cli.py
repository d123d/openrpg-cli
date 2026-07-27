"""SRD CLI command surface."""

from __future__ import annotations

import json
import secrets
import sys
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from srd_cli import __version__
from srd_cli.data import SRDRepository, category_name, get_repository
from srd_cli.dice import GameRNG, roll as roll_dice
from srd_cli.api import get_rules_api
from srd_cli.character import AbilityScores
from srd_cli.character_builder import CharacterBuilder, CharacterRequest, ChoiceError
from srd_cli.character_sheet import render_json, render_sheet
from srd_cli.character_store import CharacterStore, CharacterValidationError
from srd_cli.combat import CombatError
from srd_cli.combat_session import CombatSession, render_combat_json, render_transcript

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(errors="replace")

app = typer.Typer(
    name="srd",
    help="Browse verified SRD 5.2.1 content. No campaign-setting or third-party content.",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()
character_app = typer.Typer(help="Create, inspect, list, and validate level-1 characters.")
app.add_typer(character_app, name="character")


def _repo() -> SRDRepository:
    return get_repository()


def _character_services(root: Path | None = None) -> tuple[CharacterBuilder, CharacterStore]:
    builder = CharacterBuilder(get_rules_api())
    return builder, CharacterStore(builder, root=root)


def _fail_character(exc: Exception) -> None:
    Console(stderr=True).print(f"Error: {exc}", markup=False)
    raise typer.Exit(2)


@app.command()
def combat(
    character: Path = typer.Option(..., exists=True, readable=True),
    monster: str = typer.Option(...),
    seed: int = typer.Option(...),
    auto: bool = typer.Option(False, "--auto"),
    as_json: bool = typer.Option(False, "--json"),
    max_rounds: int = typer.Option(100, min=1, max=10_000),
) -> None:
    """Run deterministic one-character combat."""
    _, store = _character_services()
    try:
        hero = store.load(character)
        creature = get_rules_api().get_creature(monster)
        if creature is None:
            raise CombatError(f"unknown or ambiguous creature: {monster}")
        session = CombatSession(hero, creature, seed, max_rounds)
        if not auto:
            console.print("Interactive combat uses stable first legal action each turn.")
        result = session.run_auto()
        console.print(render_combat_json(result) if as_json else render_transcript(result),
                      end="", markup=False)
    except (CombatError, CharacterValidationError, OSError, ValueError) as exc:
        _fail_character(exc)


@app.command()
def play(
    character: Path | None = typer.Option(None),
    monster: str | None = typer.Option(None),
    seed: int = typer.Option(0),
) -> None:
    """Guide create/load → SRD creature → combat result."""
    builder, store = _character_services()
    try:
        if character is None:
            mode = typer.prompt("Character: create or load", default="load").strip().casefold()
            if mode == "create":
                hero = builder.build(CharacterRequest(
                    typer.prompt("Name"),
                    _pick("Class", None, builder.classes),
                    _pick("Species", None, builder.species),
                    _pick("Background", None, builder.backgrounds),
                    _pick("Feat", None, builder.feats),
                    None, (), (),
                ))
                if typer.confirm("Save character?", default=False):
                    store.save(hero)
            elif mode == "load":
                character = Path(typer.prompt("Character file"))
                hero = store.load(character)
            else:
                raise ValueError("expected create or load")
        else:
            hero = store.load(character)
        selected = monster or typer.prompt("SRD creature")
        creature = get_rules_api().get_creature(selected)
        if creature is None:
            raise CombatError(f"unknown or ambiguous creature: {selected}")
        result = CombatSession(hero, creature, seed).run_auto()
        console.print(render_transcript(result), end="", markup=False)
    except (CombatError, CharacterValidationError, ChoiceError, OSError, ValueError) as exc:
        _fail_character(exc)


def _pick(label: str, value: str | None, choices) -> str:
    if value is not None:
        return value
    names = [x.name for x in choices]
    console.print(f"{label} choices: {', '.join(names)}")
    return typer.prompt(label)


@character_app.command("create")
def character_create(
    name: str | None = typer.Option(None),
    class_: str | None = typer.Option(None, "--class"),
    species: str | None = typer.Option(None),
    background: str | None = typer.Option(None),
    feat: str | None = typer.Option(None),
    scores: str | None = typer.Option(None, help="STR,DEX,CON,INT,WIS,CHA."),
    equipment: list[str] | None = typer.Option(None, "--equipment"),
    spell: list[str] | None = typer.Option(None, "--spell"),
    output: Path | None = typer.Option(None),
    root: Path | None = typer.Option(None),
    as_json: bool = typer.Option(False, "--json"),
    overwrite: bool = typer.Option(False),
) -> None:
    """Create and save a legal deterministic level-1 character."""
    builder, store = _character_services(root)
    try:
        actual_name = name if name is not None else typer.prompt("Name")
        class_ = _pick("Class", class_, builder.classes)
        species = _pick("Species", species, builder.species)
        background = _pick("Background", background, builder.backgrounds)
        feat = _pick("Feat", feat, builder.feats)
        parsed_scores = None
        if scores:
            parts = [x.strip() for x in scores.split(",")]
            if len(parts) != 6:
                raise ValueError("scores: expected six comma-separated integers in STR,DEX,CON,INT,WIS,CHA order")
            try:
                parsed_scores = AbilityScores(*(int(x) for x in parts))
            except (ValueError, TypeError) as exc:
                raise ValueError(f"scores: {exc}") from exc
        character = builder.build(CharacterRequest(
            actual_name, class_, species, background, feat, parsed_scores,
            tuple(equipment or ()), tuple(spell or ()),
        ))
        path = store.save(character, output, overwrite=overwrite)
    except (ChoiceError, CharacterValidationError, OSError, ValueError) as exc:
        _fail_character(exc)
    if as_json:
        console.print(render_json(character), end="", markup=False)
    else:
        render_sheet(character, console)
        console.print(f"Saved: {path}")


def _character_path(store: CharacterStore, value: str) -> Path:
    candidate = Path(value)
    return candidate if candidate.is_absolute() or candidate.parent != Path(".") else store.resolve_name(value)


@character_app.command("show")
def character_show(
    file_or_name: str,
    root: Path | None = typer.Option(None),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Validate and render a saved character."""
    _, store = _character_services(root)
    try:
        character = store.load(_character_path(store, file_or_name))
    except (OSError, ValueError) as exc:
        _fail_character(exc)
    if as_json:
        console.print(render_json(character), end="", markup=False)
    else:
        render_sheet(character, console)


@character_app.command("list")
def character_list(root: Path | None = typer.Option(None), as_json: bool = typer.Option(False, "--json")) -> None:
    """List character files and validation state."""
    _, store = _character_services(root)
    rows = store.list()
    if as_json:
        console.print(json.dumps([
            {"name": x.name, "class": x.class_name, "species": x.species_name,
             "path": str(x.path), "valid": x.valid, "error": x.error}
            for x in rows
        ], ensure_ascii=False, indent=2, sort_keys=True), markup=False)
        return
    table = Table("Name", "Class", "Species", "Path", "State")
    for row in rows:
        table.add_row(row.name, row.class_name, row.species_name, str(row.path), "PASS" if row.valid else f"FAIL: {row.error}")
    console.print(table)


@character_app.command("validate")
def character_validate(file_or_name: str, root: Path | None = typer.Option(None)) -> None:
    """Validate schema, SRD references, and recomputed derived state."""
    _, store = _character_services(root)
    try:
        store.load(_character_path(store, file_or_name))
    except (OSError, ValueError) as exc:
        _fail_character(exc)
    console.print("[green]PASS[/green] character schema, references, and derived state are valid.")


def _print_entry(category: str, entry: dict[str, Any], *, raw: bool) -> None:
    if raw:
        payload = {key: value for key, value in entry.items() if not key.startswith("_")}
        console.print_json(json.dumps(payload, ensure_ascii=False))
        return
    name = _repo().entry_name(entry)
    table = Table(show_header=False, box=None, pad_edge=False)
    table.add_column("Field", style="bold cyan", no_wrap=True)
    table.add_column("Value")
    for key, value in entry.items():
        if key.startswith("_") or value in (None, "", [], {}):
            continue
        if isinstance(value, (dict, list)):
            rendered = json.dumps(value, ensure_ascii=False, indent=2)
        else:
            rendered = str(value)
        table.add_row(key.replace("_", " ").title(), rendered)
    console.print(Panel(table, title=f"{name} [{category}]", border_style="cyan"))


def _print_joined(category: str, name: str) -> bool:
    api = get_rules_api()
    getters = {
        "classes": api.get_class, "species": api.get_species,
        "backgrounds": api.get_background, "feats": api.get_feat,
        "spells": api.get_spell, "creatures": api.get_creature,
        "weapons": api.get_weapon,
    }
    getter = getters.get(category)
    view = getter(name) if getter else None
    if view is None:
        return False
    sections: list[tuple[str, tuple[Any, ...]]] = []
    for label in ("features", "traits", "benefits", "spells", "options", "actions", "properties"):
        values = getattr(view, label, ())
        if values:
            sections.append((label.title(), values))
    for label, values in sections:
        console.print(f"\n[bold cyan]{label}[/bold cyan]")
        for value in values:
            entity = getattr(value, "feature", None) or getattr(value, "spell", None) or \
                getattr(value, "action", None) or getattr(value, "property", None) or value
            console.print(f"  [bold]{getattr(entity, 'name', getattr(entity, 'pk', ''))}[/bold]")
            nested = getattr(value, "items", ()) or getattr(value, "attacks", ())
            for child in nested:
                console.print(f"    {child.name}")
    return True


@app.command()
def info() -> None:
    """Show version, provenance, category counts, audit state."""
    repo = _repo()
    manifest = repo.manifest()
    console.print(f"[bold]SRD CLI {__version__}[/bold]")
    console.print(f"Content: SRD {manifest['srd_version']}")
    console.print(f"Official source: {manifest['srd_official_url']}")
    console.print(f"Transform source: {manifest['source_repository']} @ {manifest['source_commit']}")
    console.print(f"License: {manifest['content_license']}")
    errors = repo.verify()
    console.print("Bundle audit: [green]PASS[/green]" if not errors else "[red]FAIL[/red]")
    for category, count in repo.stats().items():
        console.print(f"  {category}: {count}")


@app.command("categories")
def categories_command() -> None:
    """List browsable SRD categories."""
    stats = _repo().stats()
    for category, count in stats.items():
        console.print(f"{category}\t{count}")


@app.command("list")
def list_command(
    category: str = typer.Argument(..., help="Content category."),
    limit: int = typer.Option(100, min=1, max=5000, help="Maximum rows."),
) -> None:
    """List names in one SRD category."""
    try:
        key = category_name(category)
    except KeyError as exc:
        raise typer.BadParameter(str(exc)) from exc
    names = _repo().list_names(key)
    for name in names[:limit]:
        console.print(name)
    if len(names) > limit:
        console.print(f"[dim]… {len(names) - limit} more[/dim]")


@app.command()
def show(
    category: str = typer.Argument(..., help="Content category."),
    name: str = typer.Argument(..., help="Exact or unique partial name."),
    raw: bool = typer.Option(False, "--json", help="Print fields as JSON."),
) -> None:
    """Show one SRD entity."""
    try:
        key = category_name(category)
    except KeyError as exc:
        raise typer.BadParameter(str(exc)) from exc
    entry = _repo().find(key, name)
    if entry is None:
        hits = _repo().search(name, category=key, limit=10)
        if hits:
            suggestions = ", ".join(_repo().entry_name(hit) for _, hit in hits)
            console.print(f"[yellow]No unique match. Candidates:[/yellow] {suggestions}")
        raise typer.Exit(1)
    _print_entry(key, entry, raw=raw)
    if not raw:
        _print_joined(key, name)


@app.command()
def search(
    query: str = typer.Argument(..., help="Text to find."),
    category: str | None = typer.Option(None, help="Optional category filter."),
    limit: int = typer.Option(20, min=1, max=200, help="Maximum matches."),
) -> None:
    """Search SRD names and text."""
    try:
        hits = _repo().search(query, category=category, limit=limit)
    except KeyError as exc:
        raise typer.BadParameter(str(exc)) from exc
    table = Table("Category", "Name", "Source table")
    for current, entry in hits:
        table.add_row(current, _repo().entry_name(entry), str(entry.get("_table") or ""))
    console.print(table)
    if not hits:
        raise typer.Exit(1)


@app.command()
def roll(
    expression: str = typer.Argument(..., help="Dice expression, e.g. 2d6+3 or 4d6kh3."),
    seed: int | None = typer.Option(None, help="Deterministic RNG seed."),
) -> None:
    """Roll bounded dice using engine forked from dnd-cli."""
    rng = GameRNG(seed=seed if seed is not None else secrets.randbits(63))
    try:
        result = roll_dice(rng, expression)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    console.print(result.summary())


@app.command()
def audit() -> None:
    """Verify file allowlist, hashes, record counts, document ownership."""
    errors = _repo().verify()
    if errors:
        for error in errors:
            console.print(f"[red]FAIL[/red] {error}")
        raise typer.Exit(1)
    console.print("[green]PASS[/green] SRD bundle matches manifest; no foreign JSON tables.")
