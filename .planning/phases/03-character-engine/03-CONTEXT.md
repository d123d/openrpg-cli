# Phase 3: Character Engine - Context

**Gathered:** 2026-07-26
**Status:** Ready for planning
**Mode:** Autonomous

<domain>
## Phase Boundary

Build complete level-1 SRD character creation, derived stats, JSON persistence, validation, and sheet rendering. No combat loop yet.
</domain>

<decisions>
## Implementation Decisions

- Support all SRD 5.2.1 base classes, species, four backgrounds, and valid origin feats.
- Default ability generation uses SRD standard array assigned deterministically from class primary ability and save priorities; explicit six-score input supported.
- Character schema is versioned and human-readable JSON.
- Default save root is `~/.srd-cli/characters`; commands accept explicit paths for CI.
- Validate every content reference against RulesAPI on creation and load.
- Starting equipment and spells derive only from joined SRD tables. When SRD offers choices, deterministic defaults plus explicit overrides.
- Level 1 is required; structure should permit later levels without pretending unimplemented progression is complete.
- Rich sheet plus JSON output. Non-interactive creation is first-class.
</decisions>

<specifics>
## Specific Ideas

Commands: `srd character create`, `show`, `list`, `validate`. Tests use temp dirs. Provide readable candidate suggestions for invalid IDs.
</specifics>

<deferred>
## Deferred Ideas

Level-up/progression and combat belong later. No user-authored classes/species/backgrounds.
</deferred>
