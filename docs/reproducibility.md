# Reproducibility

## Fresh Clone

```powershell
git clone https://github.com/ncarberry64/Berger-Hopf-Standard-Model.git
cd Berger-Hopf-Standard-Model
git checkout release/bhsm-final-paper-v1.2.0
```

After the release is tagged, replace the branch checkout with:

```powershell
git checkout v1.2.0
```

## Install

```powershell
python -m pip install -e .
```

The project metadata is in `pyproject.toml`.

## Run Tests

```powershell
python -m pytest
```

The final release checklist records the test result for this branch. If your
local count differs, verify the branch/tag, Python environment, and working
tree cleanliness.

## Regenerating Outputs

The repository stores ledgers in `theory/`, `docs/`, and `manuscript/`. The
current release does not require retuning or recomputing constants. To audit
the frozen prediction set, inspect:

- `theory/bhsm_v1_frozen_prediction_set.md`
- `theory/bhsm_v1_frozen_prediction_set.json`
- `theory/bhsm_prediction_ledger.md`
- `docs/frozen_predictions.md`

## Frozen Sanity

The release integrity test checks required files and no invented DOI:

```powershell
python -m pytest tests/test_final_paper_release_package.py
```

## BHSM v1 Release Candidate

Run `python -m pytest -q` to reproduce the internal boundary no-fit package and comparison-layer guardrails. The final manifest is `artifacts/BHSM_COMPLETE_V1_RELEASE_CANDIDATE.json`.

## BHSM v1.0.0 Release Package

Release-package files:

- `README.md`
- `RELEASE_NOTES_v1.0.0.md`
- `CITATION.cff`
- `.zenodo.json`
- `docs/how_to_cite.md`
- `docs/release_checklist_v1.0.0.md`
- `manuscript/BHSM_v1_complete_internal_boundary_no_fit_package.md`
- `artifacts/BHSM_v1_release_manifest.json`

Focused release-package tests:

```powershell
python -m pytest -q tests/test_bhsm_v1_release_package.py
```

Full reproducibility command:

```powershell
python -m pytest -q
```

The release manifest records:

```text
empirical_derivation_inputs_used = false
boundary_predictions_modified_by_comparison = false
official_predictions_changed = false
doi = PENDING_ZENODO_RELEASE
```

PDF status for the new Markdown manuscript is recorded in the final sprint
report. If no environment-local build route is used, the manuscript Markdown is
the release artifact and PDF generation is deferred.

## BHSM v1.1.0 HEP Handoff Reproducibility

For the v1.1.0 HEP handoff package, start with:

```text
docs/hep_review_quickstart.md
docs/institutional_hep_handoff_index.md
artifacts/BHSM_v1_1_0_phase_three_consolidated_gate_status.json
```

The runtime validation path remains gated by external licensed Wolfram/FeynRules
tooling and legal MadGraph/UFO validation steps.
<!-- BHSM_FIXED_H_VARIATIONAL_FAMILY_SOLVABILITY_V6_30_4 -->
## Reproducing the v6.30.4 fixed-h solvability result

Run:

```text
python scripts/materialize_fixed_h_variational_family_solvability_v6_30_4.py
python -m pytest -q tests/test_bhsm_fixed_h_variational_family_solvability_v6_30_4.py
```

Materialize twice and require byte-identical output. The numerical
cross-check uses a 60-digit hypergeometric eigenfunction and independent
adaptive regular-pole shooting. It must reproduce `Omega2=0`,
`A2(pi/4)=-6.93876695733808`, `eta2=166.530406976114`, and a 33-node
profile discrepancy below `2e-12` in the normalized `Z5/kappa1=1`
representative.

<!-- BHSM_FIXED_H_LYAPUNOV_SCHMIDT_POTENTIAL_V6_30_5 -->
## Reproducing the v6.30.5 fixed-h reduced potential

Run:

```text
python scripts/materialize_fixed_h_lyapunov_schmidt_potential_v6_30_5.py
python -m pytest -q tests/test_bhsm_fixed_h_lyapunov_schmidt_potential_v6_30_5.py
```

Materialize twice and require byte-identical output. The two numerical
routes must reproduce `M4=21.6901302294121`,
`C_grav=394.705988442955`, the regular Dirichlet `Phi3` complement, and the
serialized certified bounds. The scale artifact must remain explicitly
negative unless a later action-derived selection of `G5` exists.

<!-- BHSM_1_0_COMPLETION_CONTRACT_V6_30_6 -->
## Reproducing the v6.30.6 completion contract

```text
python scripts/materialize_bhsm_1_0_completion_contract_v6_30_6.py
python -m pytest -q tests/test_bhsm_1_0_completion_contract_v6_30_6.py
```

Materialize twice and require byte-identical output. The contract tests
require every release blocker to carry a relevance rationale and affected
headline deliverable, every nonblocker to carry a post-1.0 category, and
external acceptance and arbitrary higher orders to remain nonblocking.
