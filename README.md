# Berger-Hopf Standard Model (BHSM)

BHSM is a frozen no-retuning geometric reinterpretation framework for
Standard Model structure. It attempts to derive particle-sector structure,
mass-ratio patterns, and no-extra-light-state constraints from Berger-Hopf
internal geometry. The internal theorem package is complete according to the
repository ledger, while empirical acceptance remains external.

## Status

```text
Final theorem package: COMPLETE
Release tag: bhsm-final-theorem-v1.0
Tests: 757 passed
Frozen outputs: unchanged
Zenodo DOI: pending
```

Important caution: this release is an internal theorem-package completion and
reproducibility artifact. It is not a claim of experimental confirmation or an
accepted replacement of the Standard Model.

## Quick Links

- [Final paper PDF](manuscript/BHSM_final_paper.pdf)
- [Final paper Markdown](manuscript/BHSM_final_paper.md)
- [Final theorem status](theory/full_bhsm_theorem_completion_report.md)
- [Frozen prediction ledger](theory/bhsm_v1_frozen_prediction_set.md)
- [Reproducibility instructions](docs/reproducibility.md)
- [Release notes](RELEASE_NOTES.md)
- [Citation instructions](CITATION.cff)
- [License/status](LICENSE.md)

## Where to Start

- For non-specialists: [plain-language overview](docs/BHSM_plain_language_overview.md)
- For physicists: [final paper PDF](manuscript/BHSM_final_paper.pdf)
- For theorem reviewers: [reviewer attack guide](docs/reviewer_attack_guide.md)
- For reproducibility: [reproducibility guide](docs/reproducibility.md)
- For frozen predictions: [frozen predictions guide](docs/frozen_predictions.md)
- For claim status: [claim status table](docs/claim_status_table.md)
- For limitations: [external validation notes](docs/limitations_and_external_validation.md)

## Repository Map

| Path | Purpose |
| --- | --- |
| `src/` | theorem/model code |
| `tests/` | regression and guard tests |
| `theory/` | theorem ledger and status files |
| `manuscript/` | final paper sources and PDF |
| `docs/` | reader and reviewer guides |

## Final Theorem Status

| Node | Status |
| --- | --- |
| Complete operator identification | `PROVEN` |
| Action uniqueness | `PROVEN` |
| Projector commutator control | `PROVEN` |
| Projector graph-domain stability | `PROVEN` |
| H_T lower-bound transfer | `PROVEN` |
| Index theorem | `PROVEN` |
| Mirror exclusion | `PROVEN` |
| Full H_T theorem | `PROVEN` |
| Full BHSM theorem package | `COMPLETE` |

See [theorem status summary](docs/theorem_status_summary.md) and
[full theorem completion report](theory/full_bhsm_theorem_completion_report.md).

## Frozen Model

The frozen model is immutable for this release.

| Quantity | Frozen value |
| --- | --- |
| Bare branch | `BHSM_BARE_V1` |
| Dressed candidate branch | `BHSM_DRESSED_V1_CANDIDATE` |
| Canonical geometry | `a = 1.157054135733433` |
| Universal overlap width | `S = 0.07957747154594767` |
| Virtual dressing rule | `Z_virt^{u,2}=1/2` for `c/t` only |

The dressed candidate changes only `c/t`; it leaves `u/t`, CKM
`sin_theta_13`, down-sector ratios, lepton ratios, gauge outputs,
Higgs/electroweak outputs, H_T status, and scalar outputs unchanged.

## Frozen Prediction Snapshot

| Quantity | `BHSM_BARE_V1` | `BHSM_DRESSED_V1_CANDIDATE` | Changed |
| --- | --- | --- | --- |
| `c/t` | `0.008310500554068288` | `0.004155250277034144` | `True` |
| `u/t` | `1.2690463017606151e-05` | `1.2690463017606151e-05` | `False` |
| `s/b` | `0.021933971495439474` | `0.021933971495439474` | `False` |
| `d/b` | `0.0011165200546001757` | `0.0011165200546001757` | `False` |
| `sin_theta_13` | `0.0035623676140463315` | `0.0035623676140463315` | `False` |

For the fuller model-output ledger, see
[docs/frozen_predictions.md](docs/frozen_predictions.md) and
[theory/bhsm_prediction_ledger.md](theory/bhsm_prediction_ledger.md).

## Reproduce

```powershell
python -m pytest -q
```

Expected final release result: `757 passed`.

If your local result differs, see [docs/reproducibility.md](docs/reproducibility.md).

## Claims Boundary

Allowed:

- completed internal theorem package according to the repository ledger;
- frozen predictions unchanged;
- reproducible release package;
- final paper attached.

Not allowed:

- experimentally confirmed replacement of the Standard Model;
- accepted by the scientific community;
- proven QCD confinement;
- new particle discovery;
- guaranteed correctness.

## Citation and DOI

`CITATION.cff` exists for GitHub citation display. `.zenodo.json` exists for
Zenodo metadata. Zenodo DOI is pending unless Zenodo mints one after a GitHub
release. No DOI is invented in this repository.

## License

All rights reserved. This repository is not released under an open-source
license. See [LICENSE.md](LICENSE.md).
