"""Typer command surface for developer and AI capability discovery."""

from __future__ import annotations

import json
from dataclasses import asdict
from enum import Enum
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from .backend import get_developer_backend
from .catalog import CapabilityStatus, ExperienceDomain

dev_app = typer.Typer(
    help="Inspect AI contracts, player-experience catalog, implementation status, and schemas.",
    no_args_is_help=True,
)
console = Console()


def _plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(item) for item in value]
    return value


def _json(value: Any) -> None:
    console.print(json.dumps(_plain(value), ensure_ascii=False, indent=2, sort_keys=True),
                  markup=False, soft_wrap=True)


@dev_app.command()
def manifest() -> None:
    """Show backend identity, truth order, limits, and catalog size."""
    _json(get_developer_backend().manifest())


@dev_app.command()
def domains() -> None:
    """List every player-experience domain and descriptor counts."""
    coverage = get_developer_backend().coverage()["by_domain"]
    table = Table("Domain", "Actions", "Situations")
    for domain in ExperienceDomain:
        row = coverage[domain.value]
        table.add_row(domain.value, str(row["actions"]), str(row["situations"]))
    console.print(table)


@dev_app.command()
def actions(
    domain: ExperienceDomain | None = typer.Option(None),
    status: CapabilityStatus | None = typer.Option(None),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """List action vocabulary with exact descriptions and implementation truth."""
    values = get_developer_backend().list_actions(domain=domain, status=status)
    if as_json:
        _json([asdict(item) for item in values])
        return
    table = Table("ID", "Title", "Status", "Phase", "Description")
    for item in values:
        table.add_row(
            item.id, item.title, item.status.value, str(item.phase), item.description,
        )
    console.print(table)


@dev_app.command()
def situations(
    domain: ExperienceDomain | None = typer.Option(None),
    status: CapabilityStatus | None = typer.Option(None),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """List canonical situations a player character can experience."""
    values = get_developer_backend().list_situations(domain=domain, status=status)
    if as_json:
        _json([asdict(item) for item in values])
        return
    table = Table("ID", "Domain", "Status", "Phase", "Description")
    for item in values:
        table.add_row(
            item.id, item.domain.value, item.status.value, str(item.phase), item.description,
        )
    console.print(table)


@dev_app.command()
def show(identity: str) -> None:
    """Show one action or situation with linked interaction descriptions."""
    backend = get_developer_backend()
    item = backend.get(identity)
    if item is None:
        console.print(f"Unknown descriptor: {identity}")
        raise typer.Exit(1)
    if identity in {value.id for value in backend.situations}:
        _json(backend.situation_payload(identity))
    else:
        _json(asdict(item))


@dev_app.command()
def search(query: str, limit: int = typer.Option(20, min=1, max=200)) -> None:
    """Search action and situation ids, descriptions, goals, triggers, and stakes."""
    try:
        _json(get_developer_backend().search(query, limit=limit))
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


@dev_app.command()
def coverage() -> None:
    """Report honest implemented, partial, planned, and generic-framework coverage."""
    _json(get_developer_backend().coverage())


@dev_app.command()
def prompt(situation_id: str) -> None:
    """Generate provider-neutral controller system prompt for one situation."""
    try:
        console.print(get_developer_backend().controller_prompt(situation_id), markup=False)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


@dev_app.command()
def schemas() -> None:
    """Show public AI observation and decision contracts."""
    _json(get_developer_backend().schemas())
