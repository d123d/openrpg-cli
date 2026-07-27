"""Thin Typer composition root."""

from __future__ import annotations

import sys

import typer
from rich.console import Console

from openrpg_cli.dev.cli import dev_app

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
systems_app = typer.Typer(help="Inspect isolated rules-system packs and licensing status.")
app.add_typer(character_app, name="character")
app.add_typer(dev_app, name="dev")
app.add_typer(systems_app, name="systems")

# Import after app construction: decorators register commands on shared Typer instances.
from .commands import root as _root_commands  # noqa: E402,F401
