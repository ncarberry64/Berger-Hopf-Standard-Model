# PO-BH-53: Scalar/Topographic Boundary Variation

This stacked PR performs the PO-BH-53 closure sprint for `EXPLICIT_SCALAR_TOPOGRAPHIC_BOUNDARY_VARIATION_OPEN`.

## Changes

- Added `theory/theorem_discharge_scalar_topographic_boundary_variation.md`.
- Added closure-map object and entry for `explicit_scalar_topographic_boundary_variation`.
- Upgraded the symbolic `neutral_boundary_condition` to `DERIVED_CONDITIONAL`.
- Preserved `chi_nu_AB` and `lambda_nu` as `OPEN_LOCALIZABLE`.
- Added `tests/test_scalar_topographic_boundary_variation.py`.
- Updated status, blocker, claim, and closure-map documentation.

## Conditional Boundary Form

Under explicit fixed-background boundary assumptions, the symbolic neutral boundary condition is:

```text
n_mu partial^mu Phi
- D_A(chi_nu^{AB}D_B Phi)
+ R_nu[lambda_nu, Phi, n.grad Phi]
= 0 on partialB.
```

The `R_nu` term records the still-open normal-coupling/collar convention.

## Claim Boundary

This PR does not:

- derive numerical values for `chi_nu_AB` or `lambda_nu`;
- fit any neutral boundary object to observed neutrino masses, mass splittings, PMNS values, or anomaly/FTL data;
- claim a numerical neutrino prediction;
- claim local causality violation or experimental FTL;
- change frozen or official predictions.

The public status remains: structural architecture integrated conditional; numerical closure open.

## Validation

- Focused PO-BH-53 tests: expected to pass before merge.
- Related neutral theorem tests: expected to pass before merge.
- Full pytest suite: expected to pass before merge.
- Guardrail audits: expected to pass before merge.
