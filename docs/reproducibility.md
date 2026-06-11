# Reproducibility

## Clone

```powershell
git clone https://github.com/ncarberry64/Berger-Hopf-Standard-Model.git
cd Berger-Hopf-Standard-Model
git checkout bhsm-final-theorem-v1.0
```

## Python Environment

This repository is a Python/pytest research package. Use a recent Python 3
environment. The project metadata is in `pyproject.toml`.

Install test dependencies from the project metadata if your environment does
not already have them:

```powershell
python -m pip install -e .
```

## Run Tests

```powershell
python -m pytest -q
```

Expected final release result:

```text
757 passed
```

## Frozen Sanity

The release guard tests check:

- `BHSM_BARE_V1` unchanged;
- `BHSM_DRESSED_V1_CANDIDATE` unchanged;
- `a = 1.157054135733433` unchanged;
- `S = 0.07957747154594767` unchanged;
- dressed branch changes only `c/t`;
- `u/t` unchanged;
- CKM `sin_theta_13` unchanged.

To run only the final release guards:

```powershell
python -m pytest tests/test_final_release_package.py -q
```

## If Your Test Count Differs

First check that you are on tag `bhsm-final-theorem-v1.0`. Then check Python
and pytest versions. A different test count usually means you are on another
branch, running with a partial checkout, or using a local working tree with
extra tests.
