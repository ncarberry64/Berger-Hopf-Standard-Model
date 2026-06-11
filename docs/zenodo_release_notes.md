# BHSM Final Paper Package v1.2.0

## Release Summary

This release archives the Berger-Hopf Standard Model final paper package,
including the frozen no-retuning prediction set, claim-status ledger,
reproducibility instructions, manuscript source, and tests. BHSM is presented
as a geometric reinterpretation framework for Standard Model flavor,
couplings, and generations. Claims are conservatively categorized as
derived-conditional, verified-test, strong-screen, proxy-audit, open, or
forbidden.

## What Changed Since v1.1

- Added a final paper package under `manuscript/`.
- Added reader/reviewer docs under `docs/`.
- Added Zenodo metadata scaffold `.zenodo.json`.
- Added release-integrity test coverage.
- Preserved frozen outputs and no-retuning status.

## What Is Frozen

- `BHSM_BARE_V1`
- `BHSM_DRESSED_V1_CANDIDATE`
- `a = 1.157054135733433`
- `S = 0.07957747154594767`
- supplied mode ledger
- frozen tolerances and outputs
- `Z_virt^{u,2}=1/2` applied only to `c/t`

## How to Reproduce

```powershell
python -m pip install -e .
python -m pytest
```

## What Is Not Claimed

- No full derivation of the Standard Model from first principles.
- No proof of confinement.
- No proof of quantum gravity.
- No final replacement of the Standard Model.
- No experimental confirmation by the particle-physics community.
- No post-data retuning.

## Citation

Use `CITATION.cff`. Zenodo DOI is assigned after release archival if GitHub
integration is enabled.
