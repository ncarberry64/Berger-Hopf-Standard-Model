# PO-BH-54: Normal-Coupling Collar Convention

This stacked PR performs the PO-BH-54 closure sprint for `R_NU_NORMAL_COUPLING_COLLAR_CONVENTION_OPEN`.

## Changes

- Added `theory/theorem_discharge_normal_coupling_collar_convention.md`.
- Added closure-map objects and entries for:
  - `R_nu_normal_coupling`
  - `normal_collar_convention`
- Localized fixed-normal, symmetrized, collar, Robin, and conservative-remainder routes.
- Preserved `lambda_nu` as `OPEN_LOCALIZABLE`.
- Added `tests/test_normal_coupling_collar_convention.py`.
- Updated status, blocker, claim, and closure-map documentation.

## Scientific Status

The restricted fixed-normal route conditionally gives:

```text
R_nu = lambda_nu n.grad Phi.
```

The general collar/Robin convention remains `OPEN_LOCALIZABLE`:

```text
S_collar = int_{partialB x [0,epsilon]}
lambda_nu(rho,Y) Phi partial_rho Phi d rho dA
```

and

```text
R_nu -> A_nu Phi + B_nu n.grad Phi.
```

## Claim Boundary

This PR does not:

- derive a numerical value or function for `lambda_nu`;
- fit `R_nu`, collar convention, or Robin coefficients to observed neutrino masses, splittings, PMNS values, or anomaly/FTL data;
- claim a numerical neutrino prediction;
- claim local causality violation or experimental FTL;
- change frozen or official predictions.

The public status remains: structural architecture integrated conditional; numerical closure open.

## Validation

- Focused PO-BH-54 tests: expected to pass before merge.
- Related neutral theorem tests: expected to pass before merge.
- Full pytest suite: expected to pass before merge.
- Guardrail audits: expected to pass before merge.
