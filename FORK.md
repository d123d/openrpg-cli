# Fork Provenance

SRD CLI began 2026-07-26 as a lean fork of local `C:\AI\projects\dnd-cli`.

Retained:

- deterministic bounded dice engine (`dnd_cli/dice.py` → `srd_cli/dice.py`)
- Python 3.11+, Typer, Rich, pytest, ruff stack
- SRD-first architecture

Removed:

- official adventure adaptations
- Forgotten Realms and other campaign-setting lore
- imported 5etools bestiary
- custom adventures, NPCs, factions, deities, locations, worlds, backgrounds, species
- AI DM, saves, playtest harness, media/TUI systems
- SRD 5.1/2014 and third-party publisher datasets

Source dnd-cli working tree was not modified. SRD CLI uses a new independent Git repository.

