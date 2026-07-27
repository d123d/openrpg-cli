# Phase 4: Combat & Interactive Play - Context

**Gathered:** 2026-07-26
**Status:** Ready for planning
**Mode:** Autonomous

<domain>
## Phase Boundary

Complete deterministic one-character-versus-SRD-creature combat plus interactive and headless CLI workflows. Finish v1.0 with packaging and full verification.
</domain>

<decisions>
## Implementation Decisions

- Engine owns all combat state and RNG; rendering/CLI never mutate state directly.
- Support initiative, attacks, critical hits, damage, victory/defeat, and conditions used by implemented SRD actions/spells.
- Player weapon attacks required. Implement a bounded, clearly documented subset of offensive SRD spells that can be resolved from structured fields; unsupported spells fail readably rather than invent mechanics.
- Enemies select from legal joined SRD actions deterministically; fall back only to a rules-neutral unarmed strike when source record truly has no damaging action.
- Headless `combat --auto` emits stable transcript/JSON for CI.
- Interactive `play` guides create/load, monster selection, turns, results, and optional character save.
- No adventure, setting, NPC, quest, or generated lore content.
- Runtime stays offline and stdlib+Typer+Rich.
</decisions>

<specifics>
## Specific Ideas

Commands: `srd combat`, `srd play`. Options include character path, monster, seed, auto, JSON. Tests cover same-seed byte identity and multiple CR bands.
</specifics>

<deferred>
## Deferred Ideas

Party combat, maps, adventures, AI DM, level progression, and non-SRD content.
</deferred>
