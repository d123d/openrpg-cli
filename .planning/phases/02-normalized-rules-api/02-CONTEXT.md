# Phase 2: Normalized Rules API - Context

**Gathered:** 2026-07-26
**Status:** Ready for planning
**Mode:** Autonomous

<domain>
## Phase Boundary

Build stable typed read-only representations and relationship joins for all SRD entities needed by character creation and combat. No character or combat state yet.
</domain>

<decisions>
## Implementation Decisions

- Preserve raw JSON bundle unchanged.
- Add normalized API above `SRDRepository`.
- Stdlib dataclasses preferred; no new runtime dependency.
- Stable deterministic ordering.
- All 34 source tables must be either exposed or deliberately classified as internal.
- Existing CLI commands remain compatible; richer `show` output may use normalized views.
</decisions>

<specifics>
## Specific Ideas

Class features/items, species traits, background/feat benefits, creature traits/actions/attacks, weapon properties, spellcasting options must join by primary/parent keys.
</specifics>

<deferred>
## Deferred Ideas

Character persistence and combat state belong to later phases.
</deferred>
