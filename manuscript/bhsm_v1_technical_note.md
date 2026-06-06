# BHSM v1.0 Technical Note

## Scope

This note assembles the frozen BHSM v1.0 repository outputs into one technical
manuscript map. It is generated from existing repository source material:

- `theory/bhsm_v1_frozen_prediction_set.md`
- `theory/bhsm_v1_falsification_ledger.md`
- `theory/bhsm_model_card.md`
- `theory/bhsm_prediction_ledger.md`
- `theory/bhsm_residual_audit.md`
- `theory/virtual_dressing_adoption_audit.md`
- `manuscript/bhsm_v1_prediction_table.md`
- `manuscript/bhsm_v1_falsification_table.md`
- `manuscript/bare_vs_dressed_bhsm_table.md`

No frozen model logic is changed by the paper branch.

## Frozen Baseline

| Item | Value |
| --- | --- |
| Repository commit | `03039feb14fb4c988edce8453f6ee5b234797eb2` |
| Tag | `bhsm-v1.0-freeze` |
| Freeze tests | `269 passed` |
| Geometry | `a = alpha^{-1}/(12*pi^2)` |
| Overlap width | `S = 1/(4*pi)` |
| Bare branch | `BHSM_BARE_V1` |
| Dressed branch | `BHSM_DRESSED_V1_CANDIDATE` |

## Manuscript File Map

| File | Role |
| --- | --- |
| `title.md` | title and frozen baseline identifiers |
| `abstract.md` | compact technical abstract |
| `introduction.md` | motivation and claim discipline |
| `framework.md` | constants, mode ledger, overlap rule |
| `gauge_and_field_ledger.md` | gauge group and Standard Model field ledger |
| `flavor_predictions.md` | charged ratios and PMNS effective outputs |
| `ckm_cp_structure.md` | CKM angle and Hopf-phase CP screens |
| `gauge_higgs_electroweak.md` | gauge, Higgs, and electroweak screens |
| `ht_gap_and_scalar_sector.md` | `H_T` proxy and scalar scaffold status |
| `bare_vs_dressed_branches.md` | branch comparison and dressed candidate scope |
| `falsification_ledger.md` | F1-F9 and tolerance bands |
| `limitations.md` | open proof obligations and forbidden upgrades |
| `conclusion.md` | frozen baseline summary |

## Review Rule

This branch is for manuscript work only. It must not change frozen constants,
mode ledgers, predictions, tolerance bands, or tests.
