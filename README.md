# SRD CLI

Lean, read-only CLI for latest System Reference Document: **SRD 5.2.1**.

Project contains:

- SRD 5.2.1 structured content
- search, list, show, integrity audit
- deterministic bounded dice roller forked from dnd-cli
- deterministic one-character combat and guided terminal play

Project does **not** contain:

- campaign settings or lore
- published or custom adventures
- third-party monsters, spells, items, classes, or species
- SRD 5.1 / 2014 rules
- AI-generated bundled content

Official D&D Beyond page identifies SRD 5.2.1 as latest SRD. Bundled JSON comes only from
Open5e's `data/v2/wizards-of-the-coast/srd-2024` subtree at pinned commit recorded in
`manifest.json`.

## Install

```powershell
cd C:\AI\projects\srd-cli
py -3.14 -m pip install -e ".[dev]"
```

## Use

```powershell
py -3.14 -m srd_cli info
py -3.14 -m srd_cli categories
py -3.14 -m srd_cli list creatures --limit 20
py -3.14 -m srd_cli show spell fireball
py -3.14 -m srd_cli search "temporary hit points"
py -3.14 -m srd_cli roll 4d6kh3 --seed 42
py -3.14 -m srd_cli audit
```

Installed entry points:

```powershell
srd info
srd show creature "Goblin Warrior"
srd combat --character .\hero.json --monster "Goblin Warrior" --seed 42 --auto
srd combat --character .\hero.json --monster "Goblin Warrior" --seed 42 --auto --json
srd play --character .\hero.json --monster "Goblin Warrior" --seed 42
```

Identical character, creature, seed, and output format produce byte-identical output.
Combat stays offline. Engine resolves equipped weapon attacks and structured ordinary SRD
creature attacks. Unsupported or prose-dependent mechanics fail readably; no prose gets
converted into invented rules. Scope excludes parties, maps, adventures, settings, NPCs,
quests, progression, and non-SRD content.

## Content Gate

`srd audit` enforces:

1. every bundled JSON table appears in manifest allowlist
2. every file hash matches
3. every record count matches
4. records declaring document ownership use only `srd-2024`

Run:

```powershell
py -3.14 -m pytest -q
py -3.14 -m ruff check .
py -3.14 -m build
py -3.14 -m pytest tests/test_release_smoke.py -q
```

See `LICENSE-CONTENT.md` for required attribution. Code license not yet declared.
