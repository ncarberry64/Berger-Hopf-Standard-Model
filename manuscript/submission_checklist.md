# BHSM v1.1 Submission Checklist

Status: publication-readiness draft for the `bhsm-v1.1-paper` branch.

## Frozen Model Integrity

- [x] No `src/` model logic changed in this typesetting pass.
- [x] Frozen constants remain unchanged:
  - `a = alpha^{-1}/(12*pi^2)`
  - `S = 1/(4*pi)`
- [x] Frozen branches remain separate:
  - `BHSM_BARE_V1`
  - `BHSM_DRESSED_V1_CANDIDATE`
- [x] Dressed branch changes only `c/t`.
- [x] Dressed branch remains candidate, not final canonical adoption.
- [x] No tolerance bands changed.
- [x] No frozen prediction outputs changed.

## Manuscript Package

- [x] Unified Markdown manuscript exists:
  `manuscript/BHSM_v1_technical_note_full.md`
- [x] Verified references file exists:
  `manuscript/references.md`
- [x] LaTeX manuscript source exists:
  `manuscript/BHSM_v1_technical_note.tex`
- [x] PDF manuscript generated:
  `manuscript/BHSM_v1_technical_note.pdf`
- [x] PDF visual proofread/layout pass completed with no remaining overfull or
  underfull box warnings in the final LaTeX log.

## Required Claim Discipline

- [x] BHSM means Berger-Hopf Standard Model.
- [x] `BHSM_BARE_V1` and `BHSM_DRESSED_V1_CANDIDATE` are separate branches.
- [x] `BHSM_DRESSED_V1_CANDIDATE` changes only `c/t`.
- [x] Dressed branch remains candidate, not final canonical adoption.
- [x] `H_T` remains proxy/scaffold audited, not analytically proven.
- [x] Scalar decoupling remains scaffold audited.
- [x] `Omega_f` remains action-linked, not fully action-derived.
- [x] Precision QCD/RG matching remains open.
- [x] No-retuning rule remains central.
- [x] Falsification criteria F1-F9 are present.

## Publication Declarations

- [x] Funding statement included.
- [x] Conflicts of interest statement included.
- [x] Data availability statement included.
- [x] Code availability statement included with freeze tag and commit.
- [x] AI/tool assistance statement included.

## Remaining Before External Submission

- [ ] Select target venue or preprint format.
- [ ] Convert references to the target journal style.
- [ ] Confirm author affiliation, acknowledgements, and funding wording.
- [ ] Decide whether the private repository should be made visible, mirrored,
  archived, or cited by private-access statement.
- [ ] Perform final author/content proofread after compilation.
- [ ] Confirm whether `BHSM_DRESSED_V1_CANDIDATE` should remain candidate-only
  in the submitted version.
