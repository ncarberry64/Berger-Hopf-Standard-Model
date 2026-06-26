# BHSM Feynman Rules Status v0.1.0

BHSM v1.0.1 does not currently export a full set of collider-ready Feynman
rules.

The repository exports internal boundary/operator-level artifacts. A future
Feynman-rule layer must map those artifacts into a complete 4D Lagrangian, field
table, gauge conventions, interaction vertices, parameter card, and UFO model.

## Current Status

| Item | Status |
| --- | --- |
| Boundary/operator artifacts | Exported |
| Complete 4D collider Lagrangian | Not exported |
| Gauge fixing | Not exported |
| Field-content table for UFO | Template only |
| Parameter card | Template only |
| Vertex table | Template only |
| Feynman rules | Not exported |
| UFO/FeynRules model | Not exported |

## Required Future Work

- Define all collider fields and conventions.
- Define gauge groups and gauge-fixing choices.
- Define all physical parameters and source artifacts.
- Derive/export all interaction vertices.
- Validate a UFO/FeynRules-compatible model.
- Compare generated quantities against pinned external targets without feeding
  empirical values back into BHSM derivations.

## Phase Two-A Update

Phase Two-A adds `artifacts/BHSM_vertex_source_ledger_v0_2.json`, which is a
source ledger only. It does not export Lorentz structures, gauge-fixed vertices,
or Feynman rules.

## Phase Three-A Update

Phase Three-A adds `artifacts/BHSM_feynrules_translation_gate_v0_3.json`. The
gate remains closed: `feynrules_ready = false` and `ufo_ready = false`.
Candidate effective Lagrangian entries are not production Feynman rules.
