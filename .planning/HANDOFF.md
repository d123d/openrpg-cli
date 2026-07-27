# OpenRPG CLI Handoff

## Current state

Structural sync complete through `srd-cli@5b89831`. OpenRPG provider architecture, `systems` CLI, isolated packs, manifests, license audits, output remain intact. Machine-readable boundary: `openrpg_cli/contract_sync.json`.

## Commits

- `58cb0cd` — explicit `DeterministicRNG` / `LegacyPythonRNG`; inward `RandomSource`.
- `7c4619e` — `CommandRouter`, typed handlers, split reducer.
- `f86b9e7` — presentation CLI composition; OpenRPG `systems` commands preserved.
- `a2e84fa` — upstream/core compatibility metadata.

## Compatibility

- Upstream SRD: `51bc0b8`, `cbbb155`, `5b89831` (through `5b89831`).
- OpenRPG Core: version `0.1.0`, verified commit `c178e59`.
- Family policy: inherit shared common-system structural contracts only. Preserve distinct OpenRPG multi-system/provider scope and licensing isolation.

## Gates

- Functional: 107 tests pass excluding release smoke.
- Systems audit: 12 packs, zero errors.
- Ruff: repository has pre-existing baseline debt; validate changed paths plus `F821`.
- Release smoke/build: rerun after final docs commit; prior failure came from build backend/environment and needs captured stderr if persistent.

## Next tasks

1. Run full pytest, Ruff targeted gate, wheel build, isolated smoke.
2. Fix only regressions caused by structural sync; record baseline lint/build debt separately.
3. Begin Phase 9 SRD Effect Adapters. Do not broaden provider scope by copying SRD-only policy.
