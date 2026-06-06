# BHSM v1.1 Manuscript QA Report

Branch: `bhsm-v1.1-paper`

## Files Reviewed

Primary manuscript files:

- `manuscript/title.md`
- `manuscript/abstract.md`
- `manuscript/introduction.md`
- `manuscript/framework.md`
- `manuscript/gauge_and_field_ledger.md`
- `manuscript/flavor_predictions.md`
- `manuscript/ckm_cp_structure.md`
- `manuscript/gauge_higgs_electroweak.md`
- `manuscript/ht_gap_and_scalar_sector.md`
- `manuscript/bare_vs_dressed_branches.md`
- `manuscript/falsification_ledger.md`
- `manuscript/limitations.md`
- `manuscript/conclusion.md`
- `manuscript/bhsm_v1_technical_note.md`

Frozen source files checked for consistency:

- `theory/bhsm_v1_frozen_prediction_set.md`
- `theory/bhsm_v1_falsification_ledger.md`
- `theory/bhsm_model_card.md`
- `theory/bhsm_prediction_ledger.md`
- `theory/bhsm_residual_audit.md`
- `theory/virtual_dressing_adoption_audit.md`

## Inconsistencies Found

No numerical or branch inconsistencies were found against the frozen v1.0
prediction set.

Two negated overclaim-trigger phrases in `manuscript/limitations.md` were
reworded so the required manuscript files do not contain forbidden strings.

## Edits Made

- Standardized new manuscript wording to `Berger–Hopf Standard Model` where
  the acronym is defined.
- Reworded limitations to avoid the exact forbidden phrases while preserving
  the same conservative claim discipline.
- Added `tests/test_manuscript_qa.py` to check required files, frozen
  constants, branch distinction, dressed-only `c/t`, limitations, F1-F9, and
  forbidden phrase absence.

## Test Result

Command:

```powershell
python -m pytest -q
```

Result:

```text
275 passed
```

## Frozen Prediction Check

No frozen constants, mode ledgers, tolerances, predictions, or model tests were
changed. `BHSM_DRESSED_V1_CANDIDATE` remains separate from `BHSM_BARE_V1` and
changes only `c/t`.

## Remaining Manuscript Weaknesses

- The manuscript is a modular Markdown technical draft, not a typeset paper.
- Citations and external literature context have not been added.
- The open proof obligations remain: full analytic `H_T` spectrum,
  action-derived `Omega_f`, full scalar/topographic decoupling, and precision
  QCD/RG matching.
