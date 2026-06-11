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
