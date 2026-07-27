# Roadmap: SRD CLI — v1.0 Complete Working CLI

**Created:** 2026-07-26
**Core Value:** A complete offline 5E CLI whose bundled game content is provably limited to SRD 5.2.1.

## Milestone Hard Gates

1. Bundled content remains SRD 5.2.1 only.
2. `py -3.14 -m srd_cli audit` passes after every phase.
3. `py -3.14 -m pytest -q` and `py -3.14 -m ruff check .` pass.
4. Same seed and inputs produce identical characters, rolls, and combat.
5. No network dependency at runtime.

## Phases

- [x] **Phase 1: Clean SRD-Only Fork** - Independent repo, pinned data, attribution, audit, browse/search/show/roll CLI
- [x] **Phase 2: Normalized Rules API** - Typed joins expose complete SRD classes, species, backgrounds, feats, equipment, spells, and creatures
- [x] **Phase 3: Character Engine** - Create, inspect, save, and load legal SRD characters with deterministic derived statistics
- [x] **Phase 4: Combat & Interactive Play** - Run deterministic SRD creature combat and a complete interactive terminal workflow

## Phase Details

### Phase 1: Clean SRD-Only Fork
**Goal**: Establish independent, auditable SRD 5.2.1-only baseline.
**Depends on**: Nothing
**Requirements**: SRD-01, SRD-02, SRD-03, SRD-04, AUD-01, CLI-01, DICE-01, DEV-01
**Success Criteria**:
  1. Repository contains no campaign-setting, adventure, 2014, or third-party data.
  2. Audit validates allowlist, SHA-256 hashes, record counts, and document ownership.
  3. User can browse, search, inspect, and roll from CLI.
**Plans**: Complete in root commit `31d9534`.

### Phase 2: Normalized Rules API
**Goal**: Every core SRD entity needed by character creation and combat has a stable typed representation and relationship joins.
**Depends on**: Phase 1
**Requirements**: API-01, API-02, API-03, API-04, API-05, API-06
**Success Criteria**:
  1. User can inspect a class with joined features, starting equipment, proficiencies, and spellcasting data.
  2. Species, background, and feat benefits resolve from relationship tables.
  3. Creature actions/attacks/traits and weapon properties resolve without raw foreign keys.
  4. Public API never mutates raw source data and keeps deterministic ordering.
  5. Coverage tests exercise every bundled relationship table.
**Plans**: 4 plans

Plans:
- [x] 02-01-PLAN.md — Immutable typed models, deterministic loaders, 34-table classification
- [x] 02-02-PLAN.md — Character-facing class/species/background/feat/spell joins
- [x] 02-03-PLAN.md — Combat-facing creature/action/attack and weapon/property joins
- [x] 02-04-PLAN.md — Public RulesAPI, compatible CLI rendering, exhaustive coverage

### Phase 3: Character Engine
**Goal**: User can create, inspect, save, and load a playable SRD character.
**Depends on**: Phase 2
**Requirements**: CHAR-01, CHAR-02, CHAR-03, CHAR-04, CHAR-05, CHAR-06
**Success Criteria**:
  1. Guided and non-interactive commands create characters from SRD class, species, background, feat, equipment, and spell choices.
  2. Ability modifiers, proficiency bonus, HP, AC, saves, skills, attacks, and spell DC are derived deterministically.
  3. Invalid/non-SRD choices fail with readable suggestions.
  4. Character JSON schema is versioned; save/load round-trips without loss.
  5. `character validate` detects tampering or illegal references.
**Plans**: 4 plans

Plans:
- [x] 03-01-PLAN.md — Immutable contracts, deterministic legal choices, and derived statistics
- [x] 03-02-PLAN.md — Canonical JSON persistence and integrity validation
- [x] 03-03-PLAN.md — Rich and JSON character sheet rendering
- [x] 03-04-PLAN.md — Guided/headless character CLI workflow

### Phase 4: Combat & Interactive Play
**Goal**: User can run a complete deterministic combat session using an SRD character and SRD creatures.
**Depends on**: Phase 3
**Requirements**: COMBAT-01, COMBAT-02, COMBAT-03, COMBAT-04, COMBAT-05, PLAY-01, PLAY-02
**Success Criteria**:
  1. Combat supports initiative, movement-neutral turns, attacks, damage, critical hits, conditions, death/defeat, and victory.
  2. User can choose weapons/spells; enemies choose legal SRD actions deterministically.
  3. Seeded encounter transcript is byte-identical across runs.
  4. `srd play` provides interactive create/load → encounter → results loop.
  5. `srd combat --character ... --monster ... --seed ... --auto` runs headlessly for CI.
  6. Full audit, tests, ruff, package install, and smoke commands pass.
**Plans**: 4 plans

Plans:
- [x] 04-01-PLAN.md — Deterministic combat state, initiative, and weapon resolution
- [x] 04-02-PLAN.md — Structured offensive spells and deterministic SRD enemy actions
- [x] 04-03-PLAN.md — Reproducible sessions, transcripts, and combat CLI
- [x] 04-04-PLAN.md — Interactive play loop and installed-artifact v1.0 verification

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Clean SRD-Only Fork | 1/1 | Complete | 2026-07-26 |
| 2. Normalized Rules API | 4/4 | Complete | 2026-07-26 |
| 3. Character Engine | 4/4 | Complete | 2026-07-26 |
| 4. Combat & Interactive Play | 4/4 | Complete | 2026-07-26 |
