# BHSM To UFO Mapping v0.2

The mapping direction is:

```text
BHSM internal boundary artifacts
-> analytical export ledgers
-> future 4D Lagrangian and Feynman-rule layer
-> future UFO model
```

The current sprint only implements the analytical export-ledger step. It does
not invent the missing 4D Lagrangian, Feynman rules, Lorentz structures, field
normalizations, or vertex normalizations.

## Current Mapping Classes

- `EXPORTED_INTERNAL_BHSM_ARTIFACT`: value exists in an exported repo artifact.
- `SYMBOLIC_MAPPING_ONLY`: sector/source category exists, but no collider field
  or vertex rule exists.
- `CONDITIONAL_MAPPING`: source exists but needs a future convention bridge.
- `BLOCKED_BY_MISSING_4D_LAGRANGIAN`: no 4D collider Lagrangian exists.
- `BLOCKED_BY_MISSING_FEYNMAN_RULE`: no Feynman rule exists.
- `BLOCKED_BY_MISSING_VERTEX_NORMALIZATION`: no UFO vertex normalization exists.
- `NOT_FOR_UFO_EXPORT`: source is bookkeeping/comparison-only.

## Phase Three-A Extension

Phase Three-A extends the Phase Two-A mapping with a candidate 4D effective
Lagrangian ledger and normalization gates.

The current map is:

```text
BHSM boundary/operator artifacts
-> analytical export ledgers
-> candidate effective Lagrangian term ledger
-> field/vertex normalization ledgers
-> FeynRules translation gate
-> UFO readiness gate
```

The final two gates remain false. No production UFO directory is exported.

See:

```text
artifacts/BHSM_effective_lagrangian_candidate_v0_3.json
artifacts/BHSM_field_normalization_ledger_v0_3.json
artifacts/BHSM_vertex_normalization_ledger_v0_3.json
artifacts/BHSM_feynrules_translation_gate_v0_3.json
```
