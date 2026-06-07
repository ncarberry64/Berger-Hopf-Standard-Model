# BHSM v1.1 Final Author Review Checklist

Branch: `bhsm-v1.1-paper`

Primary files for review:

- `manuscript/BHSM_v1_technical_note.pdf`
- `manuscript/BHSM_v1_technical_note.tex`
- `manuscript/BHSM_v1_technical_note_full.md`
- `manuscript/references.md`

This checklist prepares the technical note for author review only. It does not
change BHSM model logic, frozen predictions, constants, tolerances, branches, or
ledgers.

## Author Approval

- [ ] Title approved.
- [ ] Abstract approved.
- [ ] Author name approved.
- [ ] Affiliation/contact information approved or intentionally omitted.
- [ ] Funding statement approved.
- [ ] Conflicts of interest statement approved.
- [ ] Data availability statement approved.
- [ ] Code availability statement approved.
- [ ] AI/tool-assistance statement approved.
- [ ] Repository visibility/citation decision made.

## Scientific Claim Discipline

- [ ] BHSM is defined as Berger-Hopf Standard Model.
- [ ] `BHSM_BARE_V1` and `BHSM_DRESSED_V1_CANDIDATE` are clearly separate.
- [ ] Dressed branch changes only `c/t`.
- [ ] Dressed branch remains candidate, not final canonical adoption.
- [ ] `H_T` remains proxy/scaffold audited, not analytically proven.
- [ ] Scalar decoupling remains scaffold audited.
- [ ] `Omega_f` remains action-linked, not fully action-derived.
- [ ] Precision QCD/RG matching remains open.
- [ ] No-retuning rule remains central.
- [ ] Falsification criteria F1-F9 are present.
- [ ] No overclaim phrases are introduced.

## Visual Review

- [ ] All equations visually checked.
- [ ] Frozen constants table visually checked.
- [ ] Fixed mode ledger table visually checked.
- [ ] `BHSM_BARE_V1` prediction table visually checked.
- [ ] `BHSM_DRESSED_V1_CANDIDATE` comparison table visually checked.
- [ ] Falsification criteria table visually checked.
- [ ] Tolerance bands table visually checked.
- [ ] Open proof obligations table visually checked.
- [ ] References visually checked.
- [ ] PDF page breaks and captions approved.

## Suggested Author Review Items

These are review prompts, not applied edits.

- [ ] Decide whether to add affiliation and contact email before circulation.
- [ ] Decide whether `N. Carberry` should be expanded in the author line.
- [ ] Decide whether the repository should remain private, become public, or be
  cited as available on request.
- [ ] Decide whether to keep the PDF as a compact technical note or expand it
  toward a journal-style article.
- [ ] Decide whether to include a short nontechnical summary outside the main
  manuscript.
- [ ] Decide whether to add a venue-specific bibliography format.
- [ ] Decide whether to include appendices for the frozen prediction and
  falsification ledgers.

## Final Verification

- [ ] `python -m pytest -q` passes.
- [ ] Frozen-output spot check passes.
- [ ] PDF build succeeds after any final author wording changes.
- [ ] Final diff contains only intended manuscript or proofread files.
