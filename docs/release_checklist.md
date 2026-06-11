# BHSM v1.2.0 Release Checklist

## Repository Audit

- [x] Existing tags inspected.
- [x] `bhsm-v1.1-preprint` exists.
- [x] `v1.2.0` was not present at branch creation.
- [x] Release branch created from `origin/main`.
- [x] Main branch contains BHSM v1.0 frozen model framework.
- [x] Main branch contains BHSM v1.1 preprint package.
- [x] Main branch contains tests, prediction ledger, claim ledger, and citation metadata.
- [x] Main branch did not contain `.zenodo.json`; this release adds it.

## Claim Discipline

- [x] No new physics results invented.
- [x] Frozen prediction status preserved.
- [x] No parameter retuning.
- [x] No Zenodo DOI invented.
- [x] H_T/no-extra-light-state status remains proxy/open unless stronger evidence is present in the branch.

## Validation

- [x] Full pytest result recorded: `286 passed`.
- [x] Manuscript PDF build result recorded: `pdflatex` succeeded and produced `manuscript/BHSM_final_paper.pdf`.
- [x] Frozen sanity result recorded: bare/dressed branches, `a`, `S`, `u/t`, and CKM `sin_theta_13` unchanged; dressed branch changes only `c/t`.
- [x] Safety scan result recorded: no secrets, private correspondence, unrelated large binaries, or local/private data found.

## Remaining Notes

Any unresolved failures must be recorded here before release.
