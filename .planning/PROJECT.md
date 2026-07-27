# OpenRPG CLI

## What This Is

Complete offline 5.5e/2024 rules engine and terminal game toolkit built only from SRD
5.2.1 content. It provides deterministic character, encounter, combat, social,
exploration, activity, downtime, and campaign-state systems without bundling adventures
or campaign-setting lore.

## Core Value

Every gameplay mode uses one deterministic command/event kernel while bundled content
purity remains mechanically provable as SRD 5.2.1 only.

## Validated

- New independent repository; dnd-cli remains untouched.
- Open5e SRD-only subtree vendored and pinned.
- Manifest allowlist, SHA-256 hashes, record counts, document-id audit.
- Browse, search, inspect, roll commands.
- No campaign/adventure/setting/third-party content trees.
- Typed normalized SRD API.
- Level-1 character creation, persistence, validation, and sheets.
- Deterministic 1v1 combat, interactive play, headless transcripts, playtest agent.

## Active

- Universal deterministic command/event/replay kernel.
- Complete SRD character progression and gameplay mechanics.
- Multi-actor encounters and all core action/effect lifecycles.
- Generic scene/activity systems spanning combat and noncombat play.
- Runtime-only user-authored scene/campaign data.

## Out of Scope

- Official adventures and campaign settings.
- Non-SRD D&D content.
- SRD 5.1 / 2014 compatibility.
- Bundled lore, puzzles, quests, NPC personalities, factions, deities, or adventures.
- Claiming unsupported prose-only SRD mechanics are implemented.

## Constraints

- SRD 5.2.1 only.
- CC-BY-4.0 attribution always shipped.
- Data provenance pinned and auditable.
- Python 3.11-compatible.
- No hidden network fallback for content.
