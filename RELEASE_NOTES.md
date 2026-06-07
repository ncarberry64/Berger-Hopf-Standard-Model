# BHSM v1.1 Preprint Package Release Notes

Branch: `bhsm-v1.1-paper`

## Unreleased / Development: v1.2 Action-Origin Development

Branch: `bhsm-v1.2-action-origin`

The v1.2 development branch packages the action-origin audit for the
charged-sector boundary operators. The charged-sector operators are derived
from an explicit symbolic sector boundary functional, and that functional is
reduced from a symbolic parent internal-action scaffold. Minimality and
tested-variant uniqueness audits find the scaffold
`UNIQUE_UNDER_BHSM_AXIOMS`.

This is a development addendum only. It does not alter `BHSM_BARE_V1`,
`BHSM_DRESSED_V1_CANDIDATE`, canonical constants, frozen predictions,
tolerances, or v1.1 public release outputs. It does not claim global uniqueness
of the complete Berger-Hopf internal action.

Frozen baseline:

- Tag: `bhsm-v1.0-freeze`
- Commit: `03039feb14fb4c988edce8453f6ee5b234797eb2`
- Model branches:
  - `BHSM_BARE_V1`
  - `BHSM_DRESSED_V1_CANDIDATE`

## Included

- BHSM v1.0 frozen executable model framework.
- BHSM v1.1 technical note in Markdown, LaTeX, and PDF form.
- No-retuning prediction and falsification ledgers.
- Bare canonical branch and dressed-candidate branch.
- Manuscript appendices for constants, mode ledger, frozen outputs,
  falsification criteria, `H_T`/scalar scaffold status, and reproducibility.
- Release checklist, citation metadata, and all-rights-reserved license notice.

## Bare and Dressed Candidate Branches

`BHSM_BARE_V1` is the frozen alpha-anchored Berger-Hopf overlap model.

`BHSM_DRESSED_V1_CANDIDATE` applies `Z_virt^{u,2}=1/2` only to the middle
up-sector ratio `c/t`. It leaves `u/t`, CKM `sin_theta_13`, down-sector ratios,
lepton ratios, gauge outputs, Higgs/electroweak outputs, `H_T`, and scalar
outputs unchanged.

The dressed branch remains a candidate, not final canonical adoption.

## No-Retuning Rule

The v1.0 freeze is invalidated if `a`, `S`, the supplied mode ledger,
tolerance bands, or `Z_virt` are changed based on residuals.

## Current Limitations

- Full analytic twisted Dirac / `H_T` spectrum remains open.
- `H_T` no-extra-light-state theorem remains proxy/scaffold audited.
- Scalar/topographic decoupling remains scaffold audited, not fully proven from
  the action.
- Boundary operators `Omega_f` remain action-linked, not fully action-derived.
- Precision QCD/RG matching remains open.
- Dressed branch remains a candidate branch.

## Reproducibility

Run:

```powershell
python -m pytest -q
```

The v1.1 paper branch test status at release preparation is `281 passed`.
