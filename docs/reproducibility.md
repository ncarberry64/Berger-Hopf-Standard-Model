# Reproducibility

## Current Gate-7 carrier certificate

Run `python scripts/certify_n12_gate7_arb_interaction_taylor26_macro_maps.py
--workers 15` to materialize the 47 correlated outward Arb-string macro maps,
then run `python -m pytest
tests/test_n12_gate7_arb_interaction_taylor26_macro_maps.py
tests/test_bhsm_current_system_integration_map.py -q`.  Checkpoints are keyed
to authoritative input and implementation hashes.  Do not use binary64
component balls for global composition.

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

<!-- BHSM_SCALAR_WALL_QUARTIC_SOURCE_V6_30_7 -->
## Reproducing the v6.30.7 scalar quartic audit

```text
python scripts/materialize_scalar_wall_quartic_source_v6_30_7.py
python -m pytest -q tests/test_bhsm_scalar_wall_quartic_source_v6_30_7.py
```

Materialize twice and require byte-identical UTF-8/LF output. The tests
verify the signed normalization group, KKT rephasing, canonical invariance,
factored coefficients, provenance, selector failures, exact
branch/stability incompatibility, integrity guards, negative scale
permission, and Tier A gate update.

<!-- BHSM_CLAIM_INPUT_COMPLETION_CONSISTENCY_V6_30_8 -->
## Reproducing the v6.30.8 consistency audit

```text
python scripts/materialize_claim_input_completion_consistency_v6_30_8.py
python -m pytest -q tests/test_bhsm_claim_input_completion_consistency_v6_30_8.py
```

Materialize twice and require byte-identical UTF-8/LF output. The tests
require evidence for every retained claim; exactly one valid type per
input; strict separation of derived, calibrated, comparison, candidate,
and independent inputs; complete leaf-level frozen-output paths; explicit
absence of `lambda5`, `G5`, `Z5`, and `kappa1`; a fifteen-node release
blocker set; RB-02 narrowing; correct scale dependencies; unchanged frozen
hashes; and a non-closed canonical completion gate.

<!-- BHSM_COMPLETE_UNIFIED_PARENT_ACTION_V7_0 -->
## Reproducing the v7.0 complete unified-action attempt

```text
python scripts/materialize_complete_unified_parent_action_v7_0.py
python -m pytest -q tests/test_bhsm_complete_unified_parent_action_v7_0.py
python -m bhsm.interface master-action-status --format markdown
```

When running directly from a checkout that has not been installed, place
`src` on `PYTHONPATH` for the CLI command. Materialize twice and require
byte-identical UTF-8/LF output.

The tests cover action reality, dimensions, gauge invariance,
representation/anomaly consistency, cap orientation, GHY cancellation,
matcher variation, scalar redefinition invariance, coefficient typing,
comparison-data exclusion, no double counting, fermion Hermiticity,
charged adjoint pairing, neutral domains, D0/quartic recovery, Standard
Model term classification, deterministic artifacts, CLI status, and
frozen hashes.
## BHSM v7.1 reduction record

From an uninstalled checkout:

```powershell
$env:PYTHONPATH=(Resolve-Path 'src').Path
python scripts/materialize_covariant_bulk_boundary_reduction_functor_v7_1.py
python -m bhsm.interface master-action-status --format markdown
```

The materializer updates only the single v7.1 reduction artifact and the
canonical completion gate.

## BHSM v7.2 observable transport

From an uninstalled checkout:

```powershell
$env:PYTHONPATH=(Resolve-Path 'src').Path
python -m bhsm.interface.master_action.observable_transport --materialize
python -m bhsm.interface observable-transport-status --format json
python -m bhsm.interface observable-transport-status --format markdown
```

Materialize twice and require byte-identical UTF-8/LF output. The v7.2
artifact records the scheme, reference scale, perturbative order, active
content, threshold domain, Higgs branch, universal calibration, running
mass and CKM definitions, benchmark manifest, falsification audit, and
comparison firewall.

## BHSM v7.3 distinct-prediction campaign

From an uninstalled checkout:

```powershell
$env:PYTHONPATH=(Resolve-Path 'src').Path
python -m bhsm.interface.master_action.distinct_prediction --materialize
python -m bhsm.interface distinct-prediction-status --format json
python -m bhsm.interface distinct-prediction-status --format markdown
```

Materialize twice and require byte-identical UTF-8/LF output. The v7.3
artifact records every attempted route, exact operators/equations, typed
candidate status, rejected proxy inputs, the singular action cross-block
obstruction, and live RB-15/RB-16 status. It does not consult comparison
data or alter frozen predictions.

## BHSM v8.0 mass--curvature response

```powershell
$env:PYTHONPATH=(Resolve-Path 'src').Path
python -m bhsm.interface.master_action.mass_curvature_response --materialize
python -m bhsm.interface mass-curvature-response-status --format json
python -m bhsm.interface mass-curvature-response-status --format markdown
```

Materialize twice and require byte-identical UTF-8/LF output. The artifact
freezes and hashes the universal `I3` response before its comparison block.
The comparison is then recorded as `INVALIDATED` without changing the
prediction-freeze hash. No official v7.2 prediction or calibration changes.

## BHSM v11.3 reciprocal core-surface attachment

From an uninstalled checkout:

```powershell
$env:PYTHONPATH=(Resolve-Path 'src').Path
python scripts/materialize_reciprocal_attachment_v11_3.py
python -m bhsm.interface reciprocal-attachment-status --format json
python -m bhsm.interface attachment-character-status --format markdown
python -m bhsm.interface attachment-current-status --format markdown
python -m bhsm.interface attachment-domain-status --format markdown
python -m bhsm.interface three-mode-action-status-v11-3 --format markdown
python -m bhsm.interface mark-ii-status --format markdown
```

Run the materializer twice and require byte-identical UTF-8/LF artifacts.
The campaign updates ten v11.3 records plus the canonical completion gate and
current-status JSON. It does not change frozen predictions or turn the
conditional normalized KKT model into a physical three-mode Hessian.
