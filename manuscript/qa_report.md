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

## Earlier Manuscript Weaknesses

- Typesetting has since been added in `manuscript/BHSM_v1_technical_note.tex`.
- Literature framing and references have since been added in the manuscript and
  `manuscript/references.md`.
- The open proof obligations remain: full analytic `H_T` spectrum,
  action-derived `Omega_f`, full scalar/topographic decoupling, and precision
  QCD/RG matching.

## PDF/Layout Proofread Pass

Scope: typesetting and publication-readiness layout polish only. No model
logic, frozen predictions, constants, tolerances, branches, source outputs, or
ledgers were changed.

Files reviewed:

- `manuscript/BHSM_v1_technical_note.tex`
- `manuscript/BHSM_v1_technical_note.pdf`

Layout fixes:

- Added break-friendly macros for the frozen commit hash, repository URL,
  branch names, and DOI strings.
- Replaced raw DOI `\texttt{...}` strings with breakable DOI links.
- Converted dense tables to smaller, ragged-width columns where needed.
- Moved long CKM CP numerical outputs into display math.
- Smoothed the bare-vs-dressed branch prose to avoid an underfull line.

Build result:

- Build command:
  `pdflatex -interaction=nonstopmode -halt-on-error BHSM_v1_technical_note.tex`
- PDF generated: `manuscript/BHSM_v1_technical_note.pdf`
- Page count: 7
- Final LaTeX warning audit:
  - Overfull boxes: none
  - Underfull boxes: none
  - Fatal errors: none

Visual spot check:

- Rendered the title/abstract page and table-heavy ledger pages.
- Dense prediction, dressed-branch, falsification, and tolerance tables fit
  within the page frame after layout fixes.

Remaining publication blockers:

- Select target venue or preprint format.
- Convert references to the target journal style.
- Confirm author affiliation, acknowledgements, and funding wording.
- Decide repository visibility/citation policy.
- Perform final author/content proofread.
