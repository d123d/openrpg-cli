---
phase: 03-character-engine
plan: 01
subsystem: character-engine
tags: [dataclasses, deterministic, srd-5.2.1]
requires:
  - phase: 02-normalized-rules-api
    provides: Immutable joined SRD entities and exact lookup facade
provides:
  - Immutable level-1 character contract
  - Deterministic SRD-backed builder and derived statistics
affects: [character-persistence, character-sheet, combat]
tech-stack:
  added: []
  patterns: [frozen contracts, injected read-only RulesAPI, fail-closed adapters]
key-files:
  created: [openrpg_cli/character.py, openrpg_cli/character_builder.py, tests/test_character_builder.py]
  modified: []
key-decisions:
  - "Missing primary and casting ability source fields use exhaustive base-class adapters keyed by bundled SRD class identity."
  - "Starting weapon defaults come from exact bundled weapon names present in structured background equipment benefits."
patterns-established:
  - "Persist identity and choices; recompute derived statistics."
requirements-completed: [CHAR-01, CHAR-02, CHAR-03]
duration: 18min
completed: 2026-07-26
---

# Phase 3 Plan 1: Character Contracts and Builder Summary

**Immutable SRD-backed level-1 characters with deterministic standard-array choices and complete derived play statistics**

## Performance
- **Duration:** 18 min
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- Validates all class, species, background, origin-feat, equipment, spell, score, and level inputs.
- Produces deterministic HP, AC, saves, skills, attacks, and spellcasting statistics.
- Covers every bundled base class with stable defaults and readable candidate suggestions.

## Task Commits
1. **RED tests** - `a124352`
2. **Immutable contracts** - `7a930b4`
3. **Builder and derived stats** - `ae7e04c`

## Deviations from Plan
None - plan executed within specified level-1 boundary.

## Known Stubs
None.

## Self-Check: PASSED
Files and commits verified; character builder tests pass.
