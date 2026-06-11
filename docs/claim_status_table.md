# Claim Status Table

| Claim | Status | Where to inspect | What would falsify/break it |
| --- | --- | --- | --- |
| Frozen outputs unchanged | Guarded | `theory/bhsm_v1_frozen_prediction_set.md`, `tests/test_final_release_package.py` | Any frozen output drift or branch comparison change beyond `c/t`. |
| No-retuning status | Guarded | `README.md`, `theory/bhsm_v1_frozen_prediction_set.md` | Changing `a`, `S`, mode ledger, tolerances, outputs, or `Z_virt` based on residuals. |
| Complete operator identification | `PROVEN` | `theory/full_bhsm_theorem_completion_report.md` | Final theorem chain uses a mismatched or coordinate-first operator. |
| Action uniqueness | `PROVEN` | action-origin reports under `theory/` | A competing action scaffold survives current BHSM axioms. |
| No extra light states / H_T theorem | `PROVEN` | `theory/full_bhsm_theorem_completion_report.md` | H_T lower-bound transfer fails or depends on an open/conditional node. |
| Index theorem | `PROVEN` | index reports under `theory/`, final completion report | `dim ker D_twist != 3` or sectors are not exactly lepton/up/down. |
| Mirror exclusion | `PROVEN` | mirror reports under `theory/`, final completion report | Any mirror candidate remains protected without a frozen-ledger sector. |
| CKM/mass-ratio outputs | Frozen model outputs/screens | `theory/bhsm_prediction_ledger.md`, `docs/frozen_predictions.md` | Outputs differ without a declared new frozen release. |
| QCD/RG precision limitations | Open future precision work | `docs/limitations_and_external_validation.md`, QCD/RG reports under `theory/` | Claiming precision QCD/RG completion without validated inputs and uncertainty propagation. |
