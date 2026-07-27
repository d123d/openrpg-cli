---
phase: 07-turn-action-space-engine
plan: 01
subsystem: turns
tags: [initiative, action-economy, deterministic]
requires: [phase-05-kernel]
provides: [turn-order, action-budget, legal-command-spec]
affects: [07-03, 07-05]
key-files:
  created: [srd_cli/rules/turns.py, tests/test_turns.py]
decisions: [Stable actor-id initiative tie-break, Atomic budget rejection]
metrics: {tasks: 2, completed: 2026-07-26}
---
# Phase 7 Plan 1: Turn Economy Summary

Deterministic N-actor initiative, surprise, ownership, rounds, budgets, and legal-command contracts.

## Commits
- `ed88aef` — deterministic turn economy
- `47adf7d` — quality-gate formatting

## Deviations from Plan
None.

## Self-Check: PASSED
