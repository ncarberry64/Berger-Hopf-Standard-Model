# PO-BH-52: Neutral Boundary Tensors and Boundary Condition Localization

This stacked PR localizes the neutral boundary tensors and neutral boundary condition needed by the neutral effective action and subsurface projection geometry.

## Changes

- Added `theory/theorem_discharge_neutral_boundary_tensors.md`.
- Added closure-map objects and entries for:
  - `chi_nu_AB`
  - `lambda_nu`
  - `neutral_boundary_condition`
- Linked those objects as dependencies of `S_eff_nu` and `subsurface_projection_geometry`.
- Added focused tests in `tests/test_neutral_boundary_tensors.py`.
- Updated status, blocker, claim, and closure-map documentation.

## Scientific Status

The neutral boundary tensors are localized but not derived. The current status is:

- `chi_nu_AB`: `OPEN_LOCALIZABLE`
- `lambda_nu`: `OPEN_LOCALIZABLE`
- `neutral_boundary_condition`: `OPEN_LOCALIZABLE`

Candidate variational and subsurface-channel routes are documented, but the explicit tensor values and boundary condition still require an action-level derivation.

## Claim Boundary

This PR does not:

- fit neutral tensors or boundary conditions to observed neutrino masses, splittings, PMNS values, or anomaly data;
- claim a numerical neutrino prediction;
- claim local causality violation or experimental FTL;
- change frozen or official predictions.

The public status remains: structural architecture integrated conditional; numerical closure open.

## Validation

- Focused PO-BH-52 tests: expected to pass before merge.
- Related neutral theorem tests: expected to pass before merge.
- Full pytest suite: expected to pass before merge.
- Guardrail audits: expected to pass before merge.
