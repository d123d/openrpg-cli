# SRD CLI

## What This Is

Lean fork of dnd-cli containing only latest SRD 5.2.1 content. Initial product is a
verified compendium/search/dice CLI. Gameplay can be rebuilt incrementally against this
clean baseline without inherited adventure or setting content.

## Core Value

Content purity is mechanically provable: bundled rules data is SRD 5.2.1 only.

## Validated

- New independent repository; dnd-cli remains untouched.
- Open5e SRD-only subtree vendored and pinned.
- Manifest allowlist, SHA-256 hashes, record counts, document-id audit.
- Browse, search, inspect, roll commands.
- No campaign/adventure/setting/third-party content trees.

## Active

- Normalize richer SRD entity relationships.
- Add character creation from SRD 5.2.1.
- Add deterministic combat from SRD creatures/items/spells.
- Add runtime-only user adventures without bundling them.

## Out of Scope

- Official adventures and campaign settings.
- Non-SRD D&D content.
- SRD 5.1 / 2014 compatibility.
- AI DM and presentation stack until mechanics baseline is stable.

## Constraints

- SRD 5.2.1 only.
- CC-BY-4.0 attribution always shipped.
- Data provenance pinned and auditable.
- Python 3.11-compatible.
- No hidden network fallback for content.

