# Production Coupling Map

Machine-readable artifact:

```text
artifacts/BHSM_production_coupling_map_v0_8.json
```

## Universal Rule

```text
G_prod = G_raw / product_a sqrt(Z_a)
```

In the canonical production basis:

```text
Z_a = 1 for production fields
therefore G_prod = G_raw
```

This rule applies only when the raw BHSM coefficient has a valid 4D Lorentz
attachment, a gauge representation is assigned, the coupling scheme is defined,
and mass-width/renormalization requirements are satisfied where needed.

The map includes CKM and PMNS charged-current targets, charged boundary source
matrix, neutral operator kernel, and CP holonomy phase attachment. Blocked
targets remain `feynrules_ready = false` and `ufo_ready = false`.

## Phase Three-G Follow-On

Phase Three-G uses this map to assemble a candidate production vertex table.
The map supplies source-traced coupling families, but blocked vertices remain
blocked and no production FeynRules vertex is exported.
