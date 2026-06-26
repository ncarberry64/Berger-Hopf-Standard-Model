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
