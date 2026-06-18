## Summary

This stacked PR localizes PO-BH-55, the collar geometry package needed by the neutral normal-coupling term.

It adds explicit closure-map objects for:

- `collar_coordinate_rho`
- `collar_measure`
- `normal_orientation`
- `inner_collar_edge_condition`
- `admissible_collar_variation_data`
- `robin_coefficients_A_B`

## Scientific Status

The collar geometry package has been localized as the missing convention set for the neutral normal-coupling term. Collar coordinate, measure, orientation, edge condition, and admissible variation data are now explicit closure-map objects. Robin coefficients remain open unless a full collar convention is derived.

Status remains:

```text
STRUCTURAL_ARCHITECTURE_INTEGRATED_CONDITIONAL_NUMERICAL_CLOSURE_OPEN
```

No numerical neutrino prediction is claimed. No local causality violation or experimental FTL claim is made.

## Validation

- Focused collar geometry package tests: 11 passed
- PO-BH-54 through PO-BH-47 regression cluster: 79 passed
- Full pytest suite: 1366 passed
- Guardrail audits: passed
- Frozen predictions changed: no
- Official predictions changed: no

## Claim Boundary

This PR does not derive `lambda_nu`, collar measure, normal orientation, inner-edge condition, admissible variation data, Robin coefficients, neutrino masses, PMNS values, or any anomaly/FTL parameter.

Forbidden routes remain explicit: collar coordinate, measure, orientation, edge condition, variation data, and Robin coefficients must not be fit to neutrino masses, PMNS data, or anomaly/FTL data.
