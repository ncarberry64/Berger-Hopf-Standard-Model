# BHSM v1.1 Public Release Checklist

Branch: `bhsm-v1.1-paper`

## Build and Tests

- [x] PDF builds from `manuscript/BHSM_v1_technical_note.tex`.
- [x] Tests pass with `python -m pytest -q`.
- [x] Frozen-output spot check completed.

## Repository Safety

- [x] Public repo safety scan complete.
- [x] No API keys found by release scan.
- [x] No credentials found by release scan.
- [x] No private correspondence found by release scan.
- [x] No unrelated files found in the committed release set.
- [x] No large unexpected binaries found.
- [x] No local/private data files found in the committed release set.

## Author and Declarations

- [x] Author details confirmed for citation metadata:
  Norman P. Carberry, ORCID `https://orcid.org/0009-0000-6650-3485`.
- [x] Funding declaration included.
- [x] Conflicts declaration included.
- [x] Data availability declaration included.
- [x] Code availability declaration included.
- [x] AI/tool-assistance declaration included.
- [x] Acknowledgments included.

## Manuscript Package

- [x] References verified.
- [x] Appendix A included or explicitly present in the LaTeX technical note.
- [x] Appendix B included or explicitly present in the LaTeX technical note.
- [x] Appendix C included or explicitly present in the LaTeX technical note.
- [x] Appendix D included or explicitly present in the LaTeX technical note.
- [x] Appendix E included or explicitly present in the LaTeX technical note.
- [x] Appendix F included or explicitly present in the LaTeX technical note.

## Release Files

- [x] `README.md` public release section included.
- [x] `LICENSE.md` included with all-rights-reserved wording.
- [x] `CITATION.cff` included.
- [x] `RELEASE_NOTES.md` included.

## Frozen Model Integrity

- [x] `BHSM_BARE_V1` unchanged.
- [x] `BHSM_DRESSED_V1_CANDIDATE` unchanged.
- [x] `a = alpha^{-1}/(12*pi^2)` unchanged.
- [x] `S = 1/(4*pi)` unchanged.
- [x] Dressed branch changes only `c/t`.
- [x] `u/t` unchanged in the dressed branch.
- [x] CKM `sin_theta_13` unchanged in the dressed branch.
- [x] No model logic changed.
- [x] No frozen ledgers changed.

## Remaining Before Public Release

- [ ] Author final approval of public release wording.
- [ ] Confirm repository visibility is set to public.
- [ ] Decide whether to create a GitHub Release from `bhsm-v1.1-paper`.
- [ ] Confirm whether the all-rights-reserved license posture should remain.
