# PO-BH-47: Numerical Input Closure Map and Claim-Status Cleanup

## Summary

- Adds the PO-BH-47 numerical input closure map.
- Exposes remaining symbolic numerical inputs and forbidden fit routes.
- Updates GitHub-facing status docs with conservative public wording.
- Keeps the public status: structural architecture integrated conditional; numerical closure open.
- Does not change frozen predictions or official prediction branches.

## Files Changed

- `data/bhsm_numerical_input_closure_map.json`
- `docs/bhsm_numerical_input_closure_map.md`
- `theory/theorem_discharge_numerical_input_closure_map.md`
- `tests/test_numerical_input_closure_map.py`
- GitHub-facing status and claim documents.

## Tests Run

- `python -m pytest tests/test_numerical_input_closure_map.py`
- `python -m pytest`

## Audits Run

- `python tools/audit_forbidden_claims.py`
- `python tools/audit_bhsm_status.py`
- `python tools/audit_frozen_prediction_integrity.py`

## Validation

- Frozen predictions changed: no.
- Official predictions changed: no.
- Current status label: `STRUCTURAL_ARCHITECTURE_INTEGRATED_CONDITIONAL_NUMERICAL_CLOSURE_OPEN`.
- No numerical-closure claim is made.
- No replacement-readiness claim is made.

## Open Blockers

- `CKM_1_16_EXPONENT_NOT_DERIVED`
- `S_NU_TOPO_DERIVATION_OPEN`
- `SCALAR_TOPOGRAPHIC_DECOUPLING_OPEN`
- `HIGHER_LOOP_THRESHOLDS_OPEN`
- `NUMERICAL_MASS_RATIO_LOCK_OPEN`
- `CKM_NUMERICAL_LOCK_OPEN`
- `PMNS_NUMERICAL_LOCK_OPEN`
- `NEUTRINO_ORDERING_OPEN`
- `STABILITY_AND_COUPLING_BOUNDS_OPEN`

## Next Recommended Sprint

Derive or reject one localized numerical-closure object before comparison, preferably `CKM_1_16_EXPONENT_NOT_DERIVED` or `S_NU_TOPO_DERIVATION_OPEN`.

