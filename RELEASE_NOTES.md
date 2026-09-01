# Release Notes

## BHSM Final Theorem Package v1.3.0

Zenodo DOI: `10.5281/zenodo.20663419`

The DOI was minted by Zenodo after the GitHub v1.3.0 archival release.
Scientific/theorem contents unchanged.

## BHSM Final Paper Package v1.2.0

This release prepares a Zenodo-ready final paper package for the
Berger-Hopf Standard Model (BHSM) while preserving the frozen no-retuning
prediction set.

### Included

- Final paper Markdown, LaTeX, and PDF where local tooling supports it.
- Frozen prediction summary in `docs/frozen_predictions.md` and JSON form.
- Claim-status table using `DERIVED_CONDITIONAL`, `VERIFIED_TEST`,
  `STRONG_SCREEN`, `PROXY_AUDIT`, `OPEN`, and `FORBIDDEN`.
- Reproducibility guide.
- Falsification criteria F1-F9.
- Zenodo release notes and metadata scaffold.
- Release integrity test.

### Claim Scope

BHSM is presented as a no-retuning geometric reinterpretation framework. This
release does not claim a full derivation of the Standard Model from first
principles, QCD confinement, quantum gravity, a final Standard Model
replacement, experimental confirmation, or post-data retuning.

### Reproduce

```powershell
python -m pip install -e .
python -m pytest
```

Zenodo DOI: `10.5281/zenodo.20663419`

## BHSM v1.1 Preprint Package Release Notes

## BHSM Final Theorem Package v1.0

Branch: `bhsm-final-paper-release`

Tag: `bhsm-final-theorem-v1.0`

Release commit: the target of tag `bhsm-final-theorem-v1.0`
(`git rev-parse bhsm-final-theorem-v1.0^{commit}`).

## Included

- Completed internal BHSM theorem package.
- Final paper in Markdown, LaTeX, and PDF form.
- Frozen BHSM v1.0 executable prediction set.
- `BHSM_BARE_V1` and `BHSM_DRESSED_V1_CANDIDATE`.
- Frozen sanity checks for branch/output drift.
- All-rights-reserved license notice.
- Citation metadata.
- Zenodo-ready metadata without an invented DOI.

## Theorem Package Status

| Node | Status |
| --- | --- |
| Complete operator identification | `PROVEN` |
| Action uniqueness | `PROVEN` |
| Projector commutator control | `PROVEN` |
| Projector graph-domain stability | `PROVEN` |
| H_T lower-bound transfer | `HT_LOWER_BOUND_TRANSFER_PROVEN` |
| Index theorem | `INDEX_THEOREM_PROVEN` |
| Mirror exclusion | `MIRROR_EXCLUSION_PROVEN` |
| Full H_T theorem | `FULL_HT_THEOREM_PROVEN` |
| Full BHSM theorem package | `FULL_BHSM_THEOREM_PACKAGE_COMPLETE` |

## Frozen Sanity

- `BHSM_BARE_V1`: unchanged.
- `BHSM_DRESSED_V1_CANDIDATE`: unchanged.
- `a = 1.157054135733433`: unchanged.
- `S = 0.07957747154594767`: unchanged.
- Dressed branch changes only `c/t`.
- `u/t`: unchanged.
- CKM `sin_theta_13`: unchanged.

## Frozen Prediction Branch Comparison

| Quantity | `BHSM_BARE_V1` | `BHSM_DRESSED_V1_CANDIDATE` | Changed |
| --- | --- | --- | --- |
| `c/t` | `0.008310500554068288` | `0.004155250277034144` | `True` |
| `u/t` | `1.2690463017606151e-05` | `1.2690463017606151e-05` | `False` |
| `s/b` | `0.021933971495439474` | `0.021933971495439474` | `False` |
| `d/b` | `0.0011165200546001757` | `0.0011165200546001757` | `False` |
| `sin_theta_13` | `0.0035623676140463315` | `0.0035623676140463315` | `False` |

## Test Status

Final pytest count: `757 passed`.

## DOI Status

Zenodo DOI: pending Zenodo release. No DOI has been invented or written into
the repository.
