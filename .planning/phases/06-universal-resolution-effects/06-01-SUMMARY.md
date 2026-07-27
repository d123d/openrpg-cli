---
phase: 06-universal-resolution-effects
plan: 01
subsystem: rules
tags: [d20, rng, srd-5.2.1]
requires: [{phase: 05, provides: deterministic RNG}]
provides: [universal d20 resolver, contests, passive scores]
affects: [combat, scenes]
tech-stack: {added: [], patterns: [frozen pure rule contracts]}
key-files: {created: [openrpg_cli/rules/resolution.py, tests/test_resolution.py], modified: []}
key-decisions: ["Natural attack semantics remain typed and do not affect checks or saves."]
requirements-completed: [RES-01, RES-02]
duration: 12min
completed: 2026-07-26
---
# Phase 6 Plan 1: Universal d20 Resolution Summary
**Immutable proficiency, expertise, advantage, contest, passive-score pipeline using explicit GameRNG.**

## Accomplishments
- Complete d20 audit facts including RNG span and SRD key.
- Advantage/disadvantage collapse to at most two draws.
- SRD-key golden coverage.

## Task Commits
1. **Universal d20 resolution** - `57dae65`

## Deviations from Plan
None - plan executed exactly as written.

## Self-Check: PASSED
