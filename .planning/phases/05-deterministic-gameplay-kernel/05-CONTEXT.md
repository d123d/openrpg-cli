# Phase 5: Deterministic Gameplay Kernel - Context

**Gathered:** 2026-07-26
**Status:** Ready for planning
**Mode:** Autonomous

## Phase Boundary

Build foundation only: immutable/versioned state, typed commands/events, deterministic reducer, logs, replay, hashes, migrations, and external runtime scene payload boundary. Preserve v1 APIs through adapters. Do not add gameplay domain breadth yet.

## Decisions

- New packages follow domain → rules → engine → application → interfaces dependency direction.
- Reducer is pure except explicit GameRNG passed and returned.
- Commands/events are closed tagged unions with canonical JSON and schema version.
- Append-only session log can replay from genesis or snapshot and validates hash chain.
- User-authored runtime content carries provenance and never enters bundled SRD data root.
- Existing combat/character code remains operational via compatibility adapters during migration.
- Security: bounded payload sizes, recursion depth, event counts, safe file paths, migration allowlist.

## Deferred

Checks/effects/actions/turns belong to Phases 6–7.
