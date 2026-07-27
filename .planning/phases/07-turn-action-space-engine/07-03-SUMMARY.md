---
phase: 07-turn-action-space-engine
plan: 03
subsystem: actions
tags: [core-actions, ready, resolution]
requires: [07-01, 07-02, phase-06-resolution]
provides: [core-action-catalog, action-resolution]
affects: [07-04, 07-05]
key-files:
  created: [openrpg_cli/rules/actions.py, tests/test_actions.py]
decisions: [Closed twelve-action enum, Structured effects never inferred]
metrics: {tasks: 2, completed: 2026-07-26}
---
# Phase 7 Plan 3: Core Actions Summary

Twelve SRD core actions expose typed legality, atomic costs, targets, shared d20 resolution, and Ready lifecycle.

## Commits
- `1bd0800` — core action catalog
- `47adf7d` — quality-gate formatting

## Deviations from Plan
None.

## Self-Check: PASSED
