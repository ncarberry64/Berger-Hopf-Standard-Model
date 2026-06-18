## Summary

This stacked PR audits PO-BH-56: whether the existing complete scalar/topographic boundary-action scaffolds determine the PO-BH-55 collar geometry package.

## Scientific Status

The complete scalar/topographic collar action has been audited as the source needed to derive the collar measure, orientation, edge condition, admissible variations, and Robin coefficients. Any pieces not fixed by the existing action remain open and cannot be fitted post-comparison.

Status remains:

```text
STRUCTURAL_ARCHITECTURE_INTEGRATED_CONDITIONAL_NUMERICAL_CLOSURE_OPEN
```

The honest PO-BH-56 result is:

```text
complete_scalar_topographic_collar_action: OPEN_LOCALIZABLE
collar_measure: OPEN_LOCALIZABLE
normal_orientation: OPEN_LOCALIZABLE
inner_collar_edge_condition: OPEN_LOCALIZABLE
admissible_collar_variation_data: OPEN_LOCALIZABLE
robin_coefficients_A_B: OPEN_LOCALIZABLE
R_nu_normal_coupling: OPEN_LOCALIZABLE
```

## Validation

- Focused PO-BH-56 tests: 10 passed
- PO-BH-55 and neutral/collar regression tests: 90 passed
- Full pytest suite: 1376 passed
- Guardrail audits: passed
- Frozen predictions changed: no
- Official predictions changed: no

## Claim Boundary

This PR does not derive `L_collar`, `J(Y,rho)`, `s_n`, the inner-edge condition, admissible variation data, `A_nu`, `B_nu`, `lambda_nu`, neutrino masses, PMNS values, or any anomaly/FTL parameter.

Forbidden routes remain explicit: the complete scalar/topographic collar action, `L_collar`, `J(Y,rho)`, `s_n`, edge data, `A_nu`, or `B_nu` must not be fit to neutrino masses, PMNS data, or anomaly/FTL data.
