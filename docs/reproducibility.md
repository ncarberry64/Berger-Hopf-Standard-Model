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
