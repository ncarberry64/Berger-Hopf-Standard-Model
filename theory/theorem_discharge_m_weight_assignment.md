# Theorem Discharge: M-Weight Assignment

## 1. Mission: Full BHSM Derivation Of Standard Model Structure

The purpose of this branch is to move BHSM toward a full derivation of the Standard Model from Berger-Hopf geometry. This branch audits the missing Wigner/base/orientation weight `m` needed to promote the raw-mode Berger/Hopf harmonic scaffold into explicit internal eigenfunctions.

## 2. Previous Theorem Layers Achieved

Previous theorem-discharge layers reached the raw-mode map `k=q+2j` and candidate harmonic notation `psi_{k,j,m}`, but left `m`, the selected harmonic convention, and explicit eigenfunctions open.

## 3. PO-BH-25 Raw-Mode Harmonic Map

PO-BH-25 derived raw `(k,j)` labels from `q=k-2j`.

## 4. Why `m` Is The Next Blocker

The local feature-vector and finite-width overlap program requires explicit harmonics. The remaining Wigner/base/orientation weight `m` must be fixed by BHSM structure, not guessed.

## 5. Wigner/Hopf Harmonic Admissibility Conditions

For `D^ell_{m,n}`, `ell` must be integer or half-integer; `m,n` must be allowed weights; `|m|<=ell`; `|n|<=ell`; and weights must lie in the correct lattice.

## 6. Audit Of `ell=k/2`, `n=j`

Convention A failures:

| sector | index | k | j |
| --- | ---: | ---: | ---: |
| reference_charged | 1 | 5 | 2 |
| reference_charged | 2 | 9 | 3 |
| reference_neutral | 1 | 3 | 0 |
| reference_neutral | 2 | 3 | 1 |

## 7. Alternative Harmonic Conventions

| convention | ell | n | status | reason |
| --- | --- | --- | --- | --- |
| A: ell=k/2, n=j | `ell=k/2` | `n=j` | `FAILED_GUARDRAIL` | admissibility must hold for all modes; failures recorded |
| B: ell=k, n=j | `ell=k` | `n=j` | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | may avoid parity issue but must be derived from BHSM harmonic normalization |
| C: ell=k/2, n=j/2 | `ell=k/2` | `n=j/2` | `FAILED_GUARDRAIL` | requires derivation of fiber-weight normalization |
| D: ell=k/2, n=q/2 | `ell=k/2` | `n=q/2` | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | requires derivation tying q to the Wigner fiber/base weight |

## 8. Candidate BHSM Sources For `m`

- weak orientation sigma=2T3
- active interface w
- active/singlet side
- left/right chirality
- scalar insertion H or H_tilde
- cyclic/reference channel
- boundary orientation algebra
- charge closure Q,T3,Y
- sector orientation
- generation index

## 9. Boundary Orientation Algebra Audit

The repo contains boundary orientation, `sigma`, `T3`, `w`, charge-closure, and finite-algebra scaffolds. It does not yet contain a theorem mapping those structures to Wigner `m`.

## 10. Charge/Orientation/Chirality Audit

Charge, orientation, chirality, scalar insertion, and cyclic/reference channel data are candidate sources only. None is promoted to a selected `m` assignment here.

## 11. Candidate `m` Assignment Status

| assignment | status | reason |
| --- | --- | --- |
| `m=sigma/2` | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | requires deriving Wigner m from weak orientation |
| `m=T3` | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | same orientation source, not yet harmonic-derived |
| `m=+/-j` | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | admissibility cannot be the only selection rule |
| `m=+/-q/2` | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | requires boundary proof linking q to base weight |
| `m=orientation eigenvalue` | `OPEN` | boundary orientation algebra is not yet mapped to Wigner m |
| `m=active/singlet orientation label` | `OPEN` | side labels are not yet harmonic weights |
| `m=scalar-insertion orientation label` | `OPEN` | H/H_tilde orientation is not yet a mode weight theorem |
| `m=sector channel label` | `OPEN` | channel labels are not yet base weights |
| `m=generation-index dependent label` | `FAILED_GUARDRAIL` | would be post-hoc unless derived independently |

## 12. Harmonic Convention Status

No harmonic convention is selected as theorem-derived.

## 13. Bridge To Local Feature Vectors At `y0`

Once `m` and the convention are derived, the local feature vector is `F_{k,j,m}=(psi,d_a psi,d_a d_b psi)|_y0`.

## 14. Numerical Eigenfunction Status

Explicit eigenfunction values are not derived.

## 15. Rank-Three/Yukawa Status

Finite-width rank three and numerical Yukawa values remain open.

## 16. Non-Tautology Audit

See [M-Weight Assignment Non-Tautology Audit](m_weight_assignment_non_tautology_audit.md).

## 17. What This Achieves

This branch audits the candidate harmonic conventions and `m` sources without selecting `m` by admissibility or fit.

## 18. What Remains Before Full BHSM Replacement Claim

Replacement readiness remains false until the selected harmonic convention, `m`, explicit eigenfunctions, feature values, moment contractions, numerical Yukawa values, and mixing values are derived.

## Conclusion

This branch audits the missing m-weight assignment needed to promote the raw-mode Berger/Hopf harmonic scaffold into explicit internal eigenfunctions. The branch checks Wigner/Hopf admissibility conditions, audits candidate harmonic conventions, and identifies possible BHSM boundary/orientation sources for m. Because no theorem-derived m assignment is promoted in this branch, explicit eigenfunctions, local feature values at y0, finite-width rank-three Yukawa support, numerical Yukawa values, and replacement-level claims remain open.

## Verdict Labels

- `PO_BH_26_M_WEIGHT_ASSIGNMENT_FROM_BOUNDARY_ORIENTATION_PARTIAL`
- `M_WEIGHT_CANDIDATE_SOURCES_AUDITED`
- `WIGNER_HOPF_ADMISSIBILITY_AUDITED`
- `M_WEIGHT_ASSIGNMENT_REMAINS_OPEN`
- `SELECTED_HARMONIC_CONVENTION_REMAINS_OPEN`
- `EXPLICIT_EIGENFUNCTION_VALUES_REMAIN_OPEN`
- `RANK_THREE_YUKAWA_THEOREM_REMAINS_OPEN`
- `NUMERICAL_YUKAWA_VALUES_REMAIN_OPEN`
- `BHSM_REPLACEMENT_CLAIM_NOT_READY`
- `FROZEN_PREDICTIONS_UNCHANGED`
- `OFFICIAL_PREDICTIONS_UNCHANGED`
