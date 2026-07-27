# Roadmap: SRD CLI — v2.0 Complete Gameplay Systems

**Created:** 2026-07-26
**Core Value:** Every gameplay mode uses one deterministic command/event kernel; bundled content remains SRD 5.2.1 only.

## Hard Gates

1. No bundled adventure, setting, deity, faction, NPC, puzzle, or lore content.
2. Generic frameworks may model user-authored runtime data; they may not claim absent rules are SRD-authored.
3. Explicit adapter or explicit unsupported reason—never infer complex mechanics silently from prose.
4. Audit, pytest, Ruff, deterministic replay, wheel isolation pass every phase.
5. Existing v1 commands remain compatible.

## Phases

- [x] **Phase 5: Deterministic Gameplay Kernel** - Versioned state, typed commands/events, reducer, logs, replay, migrations
- [x] **Phase 6: Universal Resolution & Effects** - Checks, saves, contests, damage, healing, death, conditions, durations
- [ ] **Phase 7: Turn, Action & Space Engine** - N actors, action economy, core actions, reactions, range bands/grid
- [ ] **Phase 8: Complete Characters & Progression** - Levels 1–20, features, inventory, spell resources, rests
- [ ] **Phase 9: SRD Effect Adapters** - Spells, monsters, items, multiattack/recharge/traits, coverage registry
- [ ] **Phase 10: Encounters, Parties & Sessions** - Encounter lifecycle, teams, party resources, objectives, controllers
- [ ] **Phase 11: Core Noncombat Scenes** - Social, exploration, discovery, puzzles, lore, hazards, challenges
- [ ] **Phase 12: Campaign Activity Systems** - Downtime, crafting, camping, slice-of-life, factions, spiritual activities
- [ ] **Phase 13: Unified CLI & Hardening** - All-mode UX/JSON, property tests, fuzzing, coverage, docs, release

## Phase Details

### Phase 5: Deterministic Gameplay Kernel
**Goal**: All future gameplay runs through replayable typed commands/events over versioned immutable state.
**Depends on**: v1.0 complete
**Requirements**: KERN-01, KERN-02, KERN-03, KERN-04, KERN-05
**Success Criteria**:
  1. Reducer replay produces byte-identical state/event hashes.
  2. Interfaces cannot mutate authoritative state.
  3. Runtime scene payloads are stored outside bundled content and labeled user-authored.
**Plans**: 4/4 complete

### Phase 6: Universal Resolution & Effects
**Goal**: Shared resolvers implement d20 tests, damage/healing/death, conditions, and durations.
**Depends on**: Phase 5
**Requirements**: RES-01, RES-02, RES-03, RES-04, RES-05
**Success Criteria**:
  1. Checks/saves/attacks/contests share one modifier pipeline.
  2. Damage defenses, temp HP, zero HP, death saves, recovery match encoded SRD rules.
  3. All 15 bundled conditions and exhaustion have tested mechanical hooks.
**Plans**: 4/4 complete

Plans:
- [x] 06-01-PLAN.md — Shared d20 resolution and SRD golden tests
- [x] 06-02-PLAN.md — Damage, healing, zero HP, death, and recovery
- [x] 06-03-PLAN.md — Complete condition hooks and deterministic effect scheduler
- [x] 06-04-PLAN.md — Kernel integration, replay, v1 compatibility, and release gates

### Phase 7: Turn, Action & Space Engine
**Goal**: Multi-actor encounters support full core action economy and targeting.
**Depends on**: Phase 6
**Requirements**: TURN-01, TURN-02, TURN-03, TURN-04, TURN-05
**Success Criteria**:
  1. N actors/teams take legal deterministic turns with action budgets.
  2. Core actions, reactions, movement, cover, visibility, grapples, and opportunity attacks work.
  3. Range-band and optional grid targeting use same command contracts.
**Plans**: 5 plans

Plans:
- [ ] 07-01-PLAN.md — N-actor initiative, legal ownership, budgets, and legal-command contracts
- [ ] 07-02-PLAN.md — Authoritative range bands and optional grid translation
- [ ] 07-03-PLAN.md — Complete core action catalog and resolution
- [ ] 07-04-PLAN.md — Grapple, shove, reactions, cover, visibility, mounted, and underwater hooks
- [ ] 07-05-PLAN.md — Kernel integration, replay, v1 compatibility, and release gates

### Phase 8: Complete Characters & Progression
**Goal**: SRD characters work across levels 1–20 with equipment, features, spells, resources, and rests.
**Depends on**: Phase 7
**Requirements**: CHAR-20, CHAR-21, CHAR-22, CHAR-23, CHAR-24, CHAR-25
**Success Criteria**:
  1. Every base class advances 1–20 with legal subclass/feature/resource state.
  2. Inventory, currency, encumbrance, equipment, ammo, tools, languages, attunement work.
  3. Spell slots/preparation/concentration and rest recovery are deterministic.
**Plans**: TBD

### Phase 9: SRD Effect Adapters
**Goal**: Structured SRD spells, creature abilities, items, and traits execute through declarative effects.
**Depends on**: Phase 8
**Requirements**: FX-01, FX-02, FX-03, FX-04, FX-05
**Success Criteria**:
  1. Effect DSL composes attacks, saves, damage, healing, conditions, movement, areas, repetition, summons, resources.
  2. Monsters support multiattack, recharge, traits, defenses, reactions, movement, spellcasting.
  3. Coverage report names every supported and unsupported corpus mechanic.
**Plans**: TBD

### Phase 10: Encounters, Parties & Sessions
**Goal**: Users create and run persistent multi-actor encounters and parties.
**Depends on**: Phase 9
**Requirements**: ENC-01, ENC-02, ENC-03, ENC-04, ENC-05
**Success Criteria**:
  1. Encounters and parties save/resume/replay with objectives, waves, morale, group resources.
  2. Human, auto, and external controllers see same legal-command interface.
  3. Scene outcomes produce structured consequences and transitions.
**Plans**: TBD

### Phase 11: Core Noncombat Scenes
**Goal**: Shared scene engine runs social, exploration, discovery, puzzle/lore, challenge, and hazard play.
**Depends on**: Phase 10
**Requirements**: SCENE-01, SCENE-02, SCENE-03, SCENE-04, SCENE-05, SCENE-06
**Success Criteria**:
  1. Every scene exposes participants, objectives, clocks, resources, legal choices, discoveries, outcomes.
  2. Social/influence, travel/search, clues/knowledge, puzzles, hazards/challenges use universal resolution.
  3. User-authored content remains external and clearly provenance-labeled.
**Plans**: TBD

### Phase 12: Campaign Activity Systems
**Goal**: Scene engine covers downtime, crafting, camping, slice-of-life, party/faction, and spiritual activities.
**Depends on**: Phase 11
**Requirements**: SCENE-07, SCENE-08, SCENE-09, SCENE-10, SCENE-11
**Success Criteria**:
  1. Generic progress/cost/check/complication framework drives downtime, crafting, training, research, work.
  2. Camp watches, rests, foraging, cooking, conversations, and recovery work.
  3. Generic party/faction/reputation and spiritual/rite/oath/devotion state works without bundled lore.
**Plans**: TBD

### Phase 13: Unified CLI & Hardening
**Goal**: Complete engine is usable, inspectable, testable, packaged, and honest about coverage.
**Depends on**: Phase 12
**Requirements**: UX-01, UX-02, QA-01, QA-02, QA-03, QA-04
**Success Criteria**:
  1. CLI and JSON interfaces create/run/act/save/resume/replay every gameplay mode.
  2. Property, state-machine, replay, malformed-input, corpus, and golden-rule tests pass.
  3. Docs publish exact supported/unsupported matrix; release wheel passes isolated smoke.
**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|---|---:|---|---|
| 5. Deterministic Gameplay Kernel | 4/4 | Complete | 2026-07-26 |
| 6. Universal Resolution & Effects | 4/4 | Complete | 2026-07-26 |
| 7. Turn, Action & Space Engine | 0/5 | Planned | - |
| 8. Complete Characters & Progression | 0/? | Not started | - |
| 9. SRD Effect Adapters | 0/? | Not started | - |
| 10. Encounters, Parties & Sessions | 0/? | Not started | - |
| 11. Core Noncombat Scenes | 0/? | Not started | - |
| 12. Campaign Activity Systems | 0/? | Not started | - |
| 13. Unified CLI & Hardening | 0/? | Not started | - |
