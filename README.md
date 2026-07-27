# OpenRPG CLI

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
cd C:\AI\projects\openrpg-cli
py -3.14 -m pip install -e ".[dev]"
```

## Use

```powershell
py -3.14 -m openrpg_cli info
py -3.14 -m openrpg_cli categories
py -3.14 -m openrpg_cli list creatures --limit 20
py -3.14 -m openrpg_cli show spell fireball
py -3.14 -m openrpg_cli search "temporary hit points"
py -3.14 -m openrpg_cli roll 4d6kh3 --seed 42
py -3.14 -m openrpg_cli audit
```

Installed entry points:

```powershell
srd info
srd show creature "Goblin Warrior"
srd combat --character .\hero.json --monster "Goblin Warrior" --seed 42 --auto
srd combat --character .\hero.json --monster "Goblin Warrior" --seed 42 --auto --json
srd play --character .\hero.json --monster "Goblin Warrior" --seed 42
srd playtest --character .\hero.json --monster "Goblin Warrior" --seed 42
```

Identical character, creature, seed, and output format produce byte-identical output.
Combat stays offline. Engine resolves equipped weapon attacks and structured ordinary SRD
creature attacks. Unsupported or prose-dependent mechanics fail readably; no prose gets
converted into invented rules. Scope excludes parties, maps, adventures, settings, NPCs,
quests, progression, and non-SRD content.

## Autonomous Playtest Bot

Run deterministic three-seed coverage:

```powershell
py -3.14 scripts/srd_playtest_bot.py --monster "Goblin Warrior" --seeds 42,7,11
```

Bot receives public combat state plus offered legal actions. Built-in coverage controller
tries least-used actions first. Every run stays bounded and saves canonical JSON under
`playlogs/srd-playtest/` plus Markdown triage under `scores/playtest-bot/`.

Plug in any AI through JSON stdin/stdout:

```powershell
py -3.14 scripts/srd_playtest_bot.py `
  --controller py -3.14 C:\path\to\controller.py `
  --monster "Goblin Warrior" --seeds 42
```

Controller reads one observation JSON document from stdin and writes:

```json
{"action": "one offered id, label, or index", "rationale": "brief reason"}
```

Empty, multiline, invalid, failed, or timed-out controller output records warning evidence
and falls back to first deterministic legal action. Engine still resolves every roll,
damage event, HP change, and outcome.

### Matrix Coverage

```powershell
py -3.14 scripts/srd_playtest_bot.py `
  --classes Fighter,Wizard,Rogue,Cleric `
  --monsters "Goblin Warrior,Ogre" `
  --seeds 42,7,11 --turns 200 --determinism-check
```

Runner bounds matrix size, creates fresh controllers per run, replays deterministic cases,
compares mechanical fingerprints, aggregates action/interaction/outcome coverage, and writes
`matrix-latest.json` plus `matrix-latest.md`.

## General AI Developer Backend

Developer backend exposes machine-readable player-experience vocabulary without pretending
planned or generic systems are implemented:

```powershell
srd dev manifest
srd dev coverage
srd dev domains
srd dev actions --domain combat --json
srd dev situations --domain investigation --json
srd dev show combat-encounter
srd dev search "capture"
srd dev prompt investigation-mystery
srd dev schemas
```

Catalog spans character, progression, resources, combat, magic, exploration, travel,
environment, social, investigation, survival, downtime, party, world, narrative, and
system experiences. Every descriptor carries exact status, authority, roadmap phase,
requirement, targets, costs, goals, triggers, actions, and stakes.

`AgentObservation` v2 supports any scene mode with public character/context state,
objectives, constraints, recent history, and described legal actions. `AgentAction`
supports offered action/target, bounded parameters, rationale, confidence, and
non-authoritative expected effect. Engine state/events remain authoritative.

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
# OpenRPG CLI

OpenRPG CLI browses isolated, attributed tabletop rules packs. Default gameplay
provider remains verified D&D SRD 5.2.1 data.

## System packs

Pack layout:

```text
openrpg_cli/data/providers/<provider-id>/packs/<pack-id>/
  manifest.json
  NOTICE.md
  ATTRIBUTION.md
  *.json
```

Each manifest owns source-document ids, full source commit, upstream file
SHA-256, license status, local file hashes, record counts, allowlist,
attribution, and enable/quarantine state. Registry selection
returns separate `SystemPack` namespaces. It never merges rows or license
boundaries across systems.

```console
openrpg systems list
openrpg systems info srd521
openrpg systems info fate-core --json
openrpg systems audit
```

Enabled open packs: Fate Core, Fate Accelerated, Fate Condensed, Dungeon World,
Forged in the Dark SRD, and Cairn First Edition. Packs
contain compact normalized mechanics only. They exclude logos, art, trade
dress, adventures, trademarks, and setting material. Cairn's CC-BY-SA content
remains in a separate provider namespace.

`acks-core`, `mothership`, `pf2e-core`, unverified `legacy-srd`, and
`questworlds-srd` are
quarantined metadata-only entries. They cannot be selected and contain no rules
records. QuestWorlds is disabled because upstream asks users of ORC content to
include a reserved logo, while project policy forbids bundled trademarks/art.
`systems audit` checks this invariant plus attribution/legal files,
source pins, document ownership, hashes, and record counts.
