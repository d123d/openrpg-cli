---
phase: 06-universal-resolution-effects
plan: 03
subsystem: rules
tags: [conditions, effects, scheduler]
requires: [{phase: 05, provides: immutable state}]
provides: [15-condition registry, deterministic effect scheduler]
affects: [turn-engine, combat]
tech-stack: {added: [], patterns: [stable id ordered transitions]}
key-files: {created: [openrpg_cli/rules/effects.py, tests/test_effects.py], modified: []}
key-decisions: ["Unsupported prose remains explicit per condition."]
requirements-completed: [RES-05]
duration: 12min
completed: 2026-07-26
---
# Phase 6 Plan 3: Condition Effects Summary
**Exact 15-condition SRD registry plus phase/tick scheduler with stable idempotent transitions.**

## Accomplishments
- Every bundled condition maps to exact SRD key.
- Implemented hooks and unsupported clauses stay explicit.
- Due callbacks precede expiry with stable effect-id ordering.

## Task Commits
1. **Condition effects scheduler** - `1961ac0`

## Deviations from Plan
None - plan executed exactly as written.

## Self-Check: PASSED
