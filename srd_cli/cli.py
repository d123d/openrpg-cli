"""SRD CLI command surface."""

from __future__ import annotations

import json
import secrets
import sys
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from srd_cli import __version__
from srd_cli.data import SRDRepository, category_name, get_repository
from srd_cli.dice import GameRNG, roll as roll_dice

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


def _repo() -> SRDRepository:
    return get_repository()


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
