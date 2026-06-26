# Runtime Parameter Modes

Machine-readable artifact:

```text
artifacts/BHSM_runtime_parameter_modes_v0_8.json
```

## BHSM_PURE_NOFIT

`BHSM_PURE_NOFIT` is the derivation-only internal package mode. It uses only
BHSM-derived internal values and released boundary no-fit artifacts. It does
not import empirical runtime masses, widths, detector cards, or post-hoc fits.

## BHSM_COLLIDER_INTERFACE

`BHSM_COLLIDER_INTERFACE` is a future runtime detector/event comparison mode.
It may accept external masses, widths, and simulation inputs at runtime for
comparison only.

Runtime empirical values may be allowed only as simulation/comparison inputs.
They must never be used to derive or retune BHSM constants, internal boundary
coefficients, or frozen predictions.

## Phase Three-G Follow-On

Phase Three-G records runtime dependencies per candidate vertex and symbolic
Lagrangian term. Pure no-fit event generation remains blocked unless no-fit
mass-width and renormalization closures exist.
