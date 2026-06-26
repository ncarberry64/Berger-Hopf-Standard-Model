# Berger-Hopf Standard Model v1.0.0 Release Notes

Release title: Berger-Hopf Standard Model v1.0.0: Complete Internal Boundary
No-Fit Package.

Short status: internal boundary no-fit package complete; external empirical
comparison layer separate/open.

## Summary

BHSM v1.0.0 exports a complete internal boundary no-fit prediction package as
machine-readable artifacts. External empirical comparison is implemented as a
separate comparison-only layer and remains open until target data and
comparison metadata are supplied.

## What Is Complete

- Profile-scale constants are exported.
- Charged boundary outputs are exported.
- Neutral/PMNS/CKM/CP boundary outputs are exported.
- Boundary-scale transport identity is exported.
- Completion manifest is exported.
- External comparison target schema, transport layer, comparison package, and
  falsification gates are exported.

## What Is Not Claimed

- No empirical validation is claimed.
- No external survey validation is claimed.
- No exact observed particle-mass claim is made.
- Empirical data are not derivation inputs.
- Boundary predictions are not modified by comparison data.

## Core Artifacts

- `artifacts/BHSM_COMPLETE_V1_RELEASE_CANDIDATE.json`
- `artifacts/BHSM_boundary_no_fit_prediction_package_v1.json`
- `artifacts/canonical_profile_hessian_theorem_v1.json`
- `artifacts/tau_sigma_boundary_values_v1.json`
- `artifacts/profile_scale_closure_values_v1.json`
- `artifacts/charged_boundary_bridge_values_v1.json`
- `artifacts/charged_outputs_at_boundary_tau_A_local_v1.json`
- `artifacts/charged_outputs_at_boundary_tau_A_background_identity_v1.json`
- `artifacts/common_scale_boundary_transport_v1.json`
- `artifacts/neutral_operator_no_fit_output_v1.json`
- `artifacts/PMNS_no_fit_operator_output_v1.json`
- `artifacts/CKM_no_fit_operator_output_v1.json`
- `artifacts/CP_no_fit_holonomy_output_v1.json`
- `artifacts/BHSM_external_comparison_target_schema_v1.json`
- `artifacts/BHSM_external_transport_layer_v1.json`
- `artifacts/BHSM_falsification_gates_v1.json`
- `artifacts/BHSM_external_empirical_comparison_package_v1.json`
- `artifacts/BHSM_v1_release_manifest.json`

## Reproducibility

```powershell
python -m pip install -e .
python -m pytest -q
```

## Tests And Audits

PR #53:

- Focused completion tests: 9 passed
- Adjacent stack tests: 112 passed
- Full suite: 1768 passed
- Forbidden-claims audit: passed
- BHSM status audit: passed
- Frozen prediction integrity audit: passed
- Safety scan: clean; only benign checklist/test wording and variable-name hits

This release sprint adds release-package tests:

- Focused release tests: 8 passed
- Adjacent stack tests: 120 passed
- Full suite: 1776 passed
- New manuscript PDF generated successfully

## Citation / DOI

Use `CITATION.cff`. DOI status is `PENDING_ZENODO_RELEASE`; do not invent a DOI.

## External Comparison Layer

The external empirical comparison layer is comparison-only. Data-absent target
sets leave the internal package complete but externally unevaluated.
