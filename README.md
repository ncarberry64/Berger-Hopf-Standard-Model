# Berger-Hopf Standard Model (BHSM)

BHSM is a frozen no-retuning geometric reinterpretation framework for Standard
Model flavor, couplings, generations, and electroweak-scale structure. The
repository contains executable screens, ledgers, tests, and manuscript material
for auditing the framework.

This is a careful research package. It is not a claim of experimental
confirmation, community acceptance, or a final replacement of the Standard
Model.

## Current Release Preparation

```text
Release branch: release/bhsm-final-paper-v1.2.0
Version: v1.2.0
Frozen outputs: unchanged
Zenodo DOI: assigned after release archival
```

## What Is Frozen?

| Item | Frozen value |
| --- | --- |
| Bare branch | `BHSM_BARE_V1` |
| Dressed candidate branch | `BHSM_DRESSED_V1_CANDIDATE` |
| Canonical geometry | `a = 1.157054135733433` |
| Universal overlap width | `S = 0.07957747154594767` |
| Virtual dressing rule | `Z_virt^{u,2}=1/2` applied only to `c/t` |

The no-retuning rule forbids post-data changes to `a`, `S`, modes, tolerances,
frozen outputs, or `Z_virt` in order to improve residuals.

## What Should a Skeptical Reader Run First?

```powershell
python -m pip install -e .
python -m pytest
```

The tests audit frozen outputs, claim ledgers, prediction ledgers, manuscript
guardrails, and release-file presence. If your test count differs from the
release checklist, confirm that you are on the release branch or tag and that
your checkout is clean.

## Key Files

| Path | Purpose |
| --- | --- |
| `src/` | executable model, screen, and audit code |
| `tests/` | regression, guard, and release-integrity tests |
| `theory/` | machine-readable and human-readable theory ledgers |
| `manuscript/` | final paper source, generated PDF, and manuscript notes |
| `docs/` | reader, reviewer, reproducibility, and Zenodo release guides |

## Start Here

- [Final paper PDF](manuscript/BHSM_final_paper.pdf)
- [Final paper Markdown](manuscript/BHSM_final_paper.md)
- [Manuscript generation notes](manuscript/README.md)
- [Frozen predictions](docs/frozen_predictions.md)
- [Claim status table](docs/claim_status_table.md)
- [Falsification criteria](docs/falsification_criteria.md)
- [Reproducibility](docs/reproducibility.md)
- [Zenodo/GitHub release notes](docs/zenodo_release_notes.md)
- [Release checklist](docs/release_checklist.md)

## Candidate Branches and Audits

- [BHSM_MIXING_DRESSED_V1_CANDIDATE](candidates/BHSM_MIXING_DRESSED_V1_CANDIDATE.md):
  exploratory clean repair candidate for CKM 2-3 mixing; not part of the
  official frozen release.

## Completion Candidate Package

- [BHSM_FULL_COMPLETION_V1_CANDIDATE](candidates/BHSM_FULL_COMPLETION_V1_CANDIDATE.md):
  not official; frozen branches remain unchanged; candidate mechanisms live
  under `candidates/`, audits live under `audits/`, and no confirmation claim
  is made.

## Claim Boundary

Allowed claims:

- BHSM is a frozen no-retuning geometric reinterpretation framework.
- The repository contains executable prediction/screen ledgers.
- Hypercharge, anomaly, mode-selection, coupling, flavor, H_T proxy, scalar,
  and reproducibility audits are implemented with explicit statuses.
- Some results are derived-conditional, verified by tests, strong screens, or
  proxy audits as labeled.

Forbidden claims:

- a full derivation of the Standard Model from first principles;
- a proof of confinement;
- a proof of quantum gravity;
- a final replacement of the Standard Model;
- experimental confirmation by the particle-physics community;
- post-data retuning.

## Outputs and Ledgers

The frozen prediction set is defined by:

- `theory/bhsm_v1_frozen_prediction_set.md`
- `theory/bhsm_v1_frozen_prediction_set.json`
- `theory/bhsm_prediction_ledger.md`
- `theory/bhsm_prediction_ledger.json`
- `docs/frozen_predictions.md`
- `docs/frozen_predictions.json`

Claim status is summarized in:

- `docs/claim_status_table.md`
- `theory/claims_ledger.json`
- `manuscript/claims_ledger.md`

## Citation and Archival

Use `CITATION.cff` for GitHub citation display. `.zenodo.json` is included for
Zenodo metadata. Do not write a DOI manually before Zenodo assigns one.

## License

All rights reserved. See `LICENSE.md`.
