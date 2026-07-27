---
phase: 07-turn-action-space-engine
plan: 04
subsystem: tactics
tags: [grapple, opportunity, cover, environment]
requires: [07-03]
provides: [tactical-transitions, modifier-hooks]
affects: [07-05]
key-files:
  created: [openrpg_cli/rules/tactics.py, tests/test_tactics.py]
decisions: [Malformed commands reject atomically, Failed legal grapple or shove spends action]
metrics: {tasks: 2, completed: 2026-07-26}
---
# Phase 7 Plan 4: Tactical Hooks Summary

Grapple, shove, opportunity, cover, visibility, mount, and underwater hooks compose shared contracts.

## Commits
- `2ce9e25` — tactical combat hooks
- `47adf7d` — quality-gate formatting

## Deviations from Plan
None.

## Self-Check: PASSED
